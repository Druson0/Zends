# src/contract_parser.py
"""Utility to parse contract documents, extract text from PDFs, and split into overlapping chunks.

The module provides:
- ``extract_text_from_pdf`` – extracts raw text from a PDF using PyMuPDF.
- ``chunk_text`` – uses LangChain's ``RecursiveCharacterTextSplitter`` to split text into ~1000‑character chunks with overlap.
- ``parse_contract`` – simple heading‑based parser for plain‑text contracts (unchanged).
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------------------
# PDF extraction utilities
# ---------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Open a PDF file and extract all text content.

    Parameters
    ----------
    pdf_path: Path
        Path to the PDF document.

    Returns
    -------
    str
        Concatenated text from all pages, or an empty string on failure.
    """
    if not pdf_path.exists():
        print(f"Error: File {pdf_path} not found.")
        return ""
    try:
        with fitz.open(str(pdf_path)) as doc:
            text = "".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        print(f"An error occurred during PDF parsing: {e}")
        return ""

# ---------------------------------------------------------------------------
# Chunking utilities (LangChain)
# ---------------------------------------------------------------------------

def chunk_text(text: str) -> List[str]:
    """Split long text into overlapping chunks using RecursiveCharacterTextSplitter.

    The splitter first attempts to break on paragraph boundaries ("\n\n"), then
    on newlines, periods, spaces, and finally any character. Chunks are roughly
    1000 characters with a 150‑character overlap, preserving context.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=True
    )
    return text_splitter.split_text(text)

# ---------------------------------------------------------------------------
# Simple contract parser (plain‑text)
# ---------------------------------------------------------------------------

def parse_contract(text: str) -> List[Tuple[str, str]]:
    """Parse contract text into a list of (heading, content) tuples.

    Parameters
    ----------
    text: str
        The raw contract text.

    Returns
    -------
    List[Tuple[str, str]]
        A list where each item is a heading and its associated body.
    """
    heading_regex = re.compile(r"^(Article|Section|Clause)\s+\d+[\.:]?", re.IGNORECASE)
    lines = text.splitlines()
    sections: List[Tuple[str, str]] = []
    current_heading = None
    current_body = []
    for line in lines:
        if heading_regex.match(line.strip()):
            if current_heading:
                sections.append((current_heading, "\n".join(current_body).strip()))
            current_heading = line.strip()
            current_body = []
        else:
            if current_heading:
                current_body.append(line)
    if current_heading:
        sections.append((current_heading, "\n".join(current_body).strip()))
    return sections

# ---------------------------------------------------------------------------
# Execution helper for quick testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Example usage – replace with real paths as needed
    input_pdf = Path("data/contract.pdf")
    output_txt = Path("data/fixed_extracted_text.txt")

    print("Extracting PDF text...")
    raw = extract_text_from_pdf(input_pdf)
    if raw:
        print("Chunking text...")
        chunks = chunk_text(raw)
        print(f"Created {len(chunks)} chunks.")
        output_txt.write_text("\n\n".join(chunks), encoding="utf-8")
        print(f"Chunks saved to {output_txt}")
    else:
        print("No text extracted.")
