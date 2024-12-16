from pathlib import Path
import os

def find_latest_file(directory, pattern):
    """Finds the latest file matching a pattern in a directory."""
    files = list(directory.glob(pattern))
    return str(max(files, key=lambda x: x.stat().st_mtime, default=None))
