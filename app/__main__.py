"""
Entry point for running the mind-map CLI.

Usage:
    python -m app generate notes.md
    python -m app sync-positions notes.excalidraw
    python -m app lint notes.md
"""

from .cli import main

if __name__ == '__main__':
    main()

