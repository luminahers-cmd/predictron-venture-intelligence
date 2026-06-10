"""Export helpers for investment memos."""

from __future__ import annotations

import textwrap

# Cap content to keep the export single-page and avoid overly large downloads.
# Lines beyond this threshold are intentionally truncated in the PDF output.
PDF_MAX_LINES = 300


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def generate_simple_pdf(text: str) -> bytes:
    """Generate a lightweight single-page PDF without extra dependencies."""
    wrapped_lines: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(textwrap.wrap(line, width=90) or [""])

    # Keep export to a single-page lightweight PDF for Streamlit download reliability.
    display_lines = wrapped_lines[:PDF_MAX_LINES]

    commands = ["BT", "/F1 10 Tf", "50 770 Td", "14 TL"]
    for line in display_lines:
        commands.append(f"({_pdf_escape(line)}) Tj")
        commands.append("T*")
    commands.append("ET")

    # PDF text streams use Latin-1 compatible bytes in this lightweight writer.
    # Non-Latin characters are replaced to keep generation dependency-free.
    stream_data = "\n".join(commands).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n%b\nendstream" % (len(stream_data), stream_data),
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF"
        ).encode("ascii")
    )

    return bytes(pdf)
