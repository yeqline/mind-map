#!/usr/bin/env python3
"""
Simple runner script for the mindmap CLI.

Usage:
    python run.py generate ../atlas/sql/sql.md
    python run.py lint ../atlas/sql/sql.md
"""

from cli import main

if __name__ == '__main__':
    main()

