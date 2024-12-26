import hashlib
import logging
import textwrap
from typing import List

import ppdeep


def chunk_document(doc: str, chunk_size: int = 1000) -> List[str]:
    """
    Splits a document into smaller chunks.

    Parameters:
    doc (str): The text of the document.
    chunk_size (int): The maximum number of characters per chunk.

    Returns:
    List[str]: A list of document chunks.
    """
    return textwrap.wrap(doc, chunk_size)


def calculate_sha256(file_path: str) -> str:
    """
    Calculates the SHA-256 hash of a file.

    Parameters:
    file_path (str): The path to the file.

    Returns:
    str: The SHA-256 hash as a 64-character hexadecimal string.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f"Failed to calculate SHA-256 for '{file_path}': {e}")
        return ""


def calculate_fuzzy_hash(file_path: str) -> str:
    """
    Calculates the Fuzzy (ppdeep) hash of a file.

    Parameters:
    file_path (str): The path to the file.

    Returns:
    str: The Fuzzy hash as a ppdeep string.
    """
    try:
        with open(file_path, "rb") as file:
            file_content = file.read()
            return ppdeep.hash(file_content)
    except Exception as e:
        logging.error(f"Failed to calculate fuzzy hash for '{file_path}': {e}")
        return ""
