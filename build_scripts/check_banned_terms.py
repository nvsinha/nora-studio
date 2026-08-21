#!/usr/bin/env python3
"""
Provenance guard.

Fails if any banned term appears in the working tree or in any git object.
This exists because the repository was migrated away from a prior owner and
must not reacquire references to it -- not in source, not in docs, not in a
commit message, not in a blob reachable from any ref.

Scanning git objects (not just the working tree) is the point: a term removed
from a file but still present in history would otherwise pass silently.

Usage:
    check_banned_terms.py [--no-git] [--terms build_scripts/banned_terms.txt]

Exit code 0 if clean, 1 if any hit.
"""

import argparse
import os
import subprocess
import sys

# Paths that legitimately contain the banned terms (this script, its list)
# and must not be scanned, or the guard would always fail against itself.
SELF_EXEMPT = {
    "build_scripts/check_banned_terms.py",
    "build_scripts/banned_terms.txt",
}

# Path prefixes excluded from BOTH the working-tree scan and the git-object
# scan. Keeping one list for both matters: SKIP_DIRS only prunes os.walk, so
# without this a path skipped on disk would still be scanned as a blob.
# This repo has no such paths today; the hook exists so all four Nora repos
# share one guard implementation.
PATH_EXEMPT_PREFIXES = ()


def is_exempt(path):
    """True if this repo-relative path is excluded from all scanning."""
    return path in SELF_EXEMPT or (
        bool(PATH_EXEMPT_PREFIXES) and path.startswith(PATH_EXEMPT_PREFIXES))


SKIP_DIRS = {".git", ".venv", "venv", "venv3", "node_modules", "__pycache__",
             ".pytest_cache", ".ruff_cache", ".mypy_cache", "dist", "build"}

BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff",
              ".woff2", ".ttf", ".otf", ".zip", ".gz", ".whl", ".so",
              ".dylib", ".mp3", ".mp4", ".svg"}


def load_terms(path):
    """Read the banned term list, ignoring blanks and # comments."""
    terms = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#"):
                terms.append(line)
    return terms


def is_scannable(name):
    """True if this filename looks like text we should read."""
    return os.path.splitext(name)[1].lower() not in BINARY_EXT


def read_text(path):
    """Return file contents, or None if it is not decodable text."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (UnicodeDecodeError, OSError):
        return None


def find_terms(text, terms, label):
    """Return a hit tuple per banned term present in text."""
    hits = []
    low = text.lower()
    for term in terms:
        if term.lower() not in low:
            continue
        line_no, snippet = 0, ""
        for i, line in enumerate(text.splitlines(), 1):
            if term.lower() in line.lower():
                line_no, snippet = i, line.strip()[:100]
                break
        hits.append((label, line_no, term, snippet))
    return hits


def iter_files(root):
    """Yield (abs_path, rel_path) for every candidate file under root."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            if is_exempt(rel) or not is_scannable(name):
                continue
            yield full, rel


def scan_working_tree(root, terms):
    """Scan every text file currently checked out."""
    hits = []
    for full, rel in iter_files(root):
        text = read_text(full)
        if text is not None:
            hits += find_terms(text, terms, rel)
    return hits


def git(root, *args):
    """Run a git command in root and return stdout as text."""
    return subprocess.run(["git", *args], cwd=root, check=False,
                          capture_output=True, text=True).stdout


def has_git(root):
    """True if root is inside a git working tree."""
    try:
        subprocess.run(["git", "rev-parse", "--git-dir"], cwd=root,
                       check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def scan_commit_metadata(root, terms):
    """Scan author names, emails, subjects and bodies of all commits."""
    log = git(root, "log", "--all", "--format=%H%x00%an%x00%ae%x00%s%x00%b")
    low = log.lower()
    return [("<git commit metadata>", 0, term, "")
            for term in terms if term.lower() in low]


def scan_blobs(root, terms):
    """Scan every blob reachable from any ref."""
    hits = []
    for line in git(root, "rev-list", "--all", "--objects").splitlines():
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        sha, name = parts
        if is_exempt(name) or not is_scannable(name):
            continue
        raw = subprocess.run(["git", "cat-file", "-p", sha], cwd=root,
                             check=False, capture_output=True).stdout
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        hits += find_terms(text, terms, f"<git blob {sha[:8]}> {name}")
    return hits


def scan_git_objects(root, terms):
    """Scan commit metadata and all reachable blobs."""
    if not has_git(root):
        print("  (no git repository -- skipping object scan)")
        return []
    return scan_commit_metadata(root, terms) + scan_blobs(root, terms)


def report(hits):
    """Print hits and return the process exit code."""
    if not hits:
        print()
        print("PASS: clean")
        return 0
    print()
    print("BANNED TERMS FOUND:")
    for path, line, term, snippet in hits:
        loc = f"{path}:{line}" if line else path
        print(f"  [{term}] {loc}")
        if snippet:
            print(f"      {snippet}")
    print()
    print(f"FAIL: {len(hits)} hit(s)")
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--terms", default="build_scripts/banned_terms.txt")
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    terms = load_terms(os.path.join(root, args.terms))
    print(f"Scanning for {len(terms)} banned terms...")

    hits = scan_working_tree(root, terms)
    print(f"  working tree : {len(hits)} hit(s)")

    if not args.no_git:
        git_hits = scan_git_objects(root, terms)
        print(f"  git objects  : {len(git_hits)} hit(s)")
        hits += git_hits

    return report(hits)


if __name__ == "__main__":
    sys.exit(main())
