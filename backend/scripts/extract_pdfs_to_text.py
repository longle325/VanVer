from __future__ import annotations

import argparse
import re
from pathlib import Path


TARGET_CHARACTER_DIRS = ("Luc_Van_Tien", "Thuy_Kieu", "Xuan_red_hair")


def discover_pdf_files(knowledge_base_dir: Path) -> list[Path]:
    """Return PDFs from the character folders that need full-text extraction."""
    pdf_files: list[Path] = []
    for directory in TARGET_CHARACTER_DIRS:
        character_dir = knowledge_base_dir / directory
        if not character_dir.exists():
            continue
        pdf_files.extend(sorted(character_dir.glob("*.pdf")))
    return sorted(pdf_files)


def build_output_path(pdf_path: Path) -> Path:
    """Write extracted text next to the PDF with a predictable suffix."""
    return pdf_path.with_name(f"{pdf_path.stem}_full_text.txt")


def normalize_text(text: str) -> str:
    """Clean common PDF extraction noise while preserving paragraph breaks."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?m)^--\s*\d+\s+of\s+\d+\s*--\s*$", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from all pages in a PDF."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: pypdf. Install with `pip install pypdf`."
        ) from exc

    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(page_text)
        else:
            pages.append(f"[Trang {index}: không trích xuất được text]")
    return normalize_text("\n\n".join(pages))


def extract_pdf_to_text(pdf_path: Path, output_path: Path | None = None) -> Path:
    """Extract a single PDF and return the generated text path."""
    output_path = output_path or build_output_path(pdf_path)
    text = extract_pdf_text(pdf_path)
    output_path.write_text(text + "\n", encoding="utf-8")
    return output_path


def extract_all(knowledge_base_dir: Path) -> list[Path]:
    """Extract all target PDFs under the knowledge base."""
    output_paths: list[Path] = []
    for pdf_path in discover_pdf_files(knowledge_base_dir):
        output_paths.append(extract_pdf_to_text(pdf_path))
    return output_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract full text from Vanver knowledge-base PDFs."
    )
    parser.add_argument(
        "--knowledge-base-dir",
        type=Path,
        default=Path("knowledge_base"),
        help="Path to backend knowledge_base directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    knowledge_base_dir = args.knowledge_base_dir.resolve()
    output_paths = extract_all(knowledge_base_dir)
    if not output_paths:
        print(f"No PDFs found under {knowledge_base_dir}")
        return 0

    for output_path in output_paths:
        print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
