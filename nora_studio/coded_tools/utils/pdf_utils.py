# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from io import BytesIO

from pypdf import PdfReader


class PdfUtils:  # pylint: disable=too-few-public-methods
    """Shared helpers for extracting text from PDF documents."""

    @staticmethod
    def parse_pdf_bytes(data: bytes) -> str:
        """Extract text from in-memory PDF bytes, joining pages with newlines."""
        reader = PdfReader(BytesIO(data))
        page_texts: list[str] = []
        for page in reader.pages:
            # extract_text() is typed Optional[str] in newer pypdf and can return
            # None for pages without extractable text (e.g. scanned images);
            # coerce to "" so the join never fails on a valid PDF.
            page_texts.append(page.extract_text() or "")
        return "\n".join(page_texts)
