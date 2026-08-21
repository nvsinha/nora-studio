# CLI reference

The `nora-studio` console script dispatches to a small set of subcommands.
Run `nora-studio --help` for the full list and shared options.

`ns` is a shorter alias for `nora-studio` — `nora run`, `nora init`, etc. work identically.

| Subcommand | Description |
|---|---|
| `run` | Start the Nora Fleet server and a client (default when no subcommand is given). |
| `init` | Scaffold a starter project in the current directory. |
| [`import`](./cli/import.md) | Import networks from nora-studio (or a `.hocon`/`.zip`) into the project. |
| [`export`](./cli/export.md) | Bundle a network from the current project into a shareable `.hocon` or `.zip`. |
| [`check-config`](./cli/check_config.md) | Validate every LLM configuration in a HOCON file. |
| [`check-llm-keys`](./cli/check_llm_keys.md) | Validate LLM API keys and other critical environment variables. |
| [`validate`](./cli/validate.md) | Validate the structure of an agent network HOCON file. |
