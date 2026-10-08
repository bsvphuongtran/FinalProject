"""Temporary upload files. The exercise validates extension and size only."""

from __future__ import annotations

import tempfile
from pathlib import Path


def write_sample(suffix: str, size: int) -> Path:
    """Write a file of the requested size and return its path."""
    directory = Path(tempfile.mkdtemp(prefix="ticket-upload-"))
    path = directory / f"sample{suffix}"
    path.write_bytes(b"\0" * size)
    return path
