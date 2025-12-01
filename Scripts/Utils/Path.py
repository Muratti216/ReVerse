import os
import sys

def _base_dirs():
    dirs = []
    try:
        if getattr(sys, 'frozen', False):
            dirs.append(os.path.dirname(sys.executable))
        # Module file location (this utils file)
        dirs.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
        # Current working directory
        dirs.append(os.getcwd())
    except Exception:
        pass
    # ensure uniqueness preserving order
    seen = set()
    out = []
    for d in dirs:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out

def asset_path(rel_path: str) -> str:
    """Resolve an asset relative path for PyInstaller one-dir layouts.

    Tries these locations in order:
    - CWD / rel_path
    - base_dir / rel_path
    - base_dir / _internal / rel_path (PyInstaller 6 layout)
    - cwd / _internal / rel_path
    Falls back to the given rel_path if nothing exists.
    """
    candidates = []
    for base in _base_dirs():
        candidates.append(os.path.join(base, rel_path))
        candidates.append(os.path.join(base, '_internal', rel_path))
    for p in candidates:
        if os.path.exists(p):
            return p
    return rel_path
