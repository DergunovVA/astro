#!/usr/bin/env python3
"""
Module entry point for running as: python -m astro
This allows the CLI to be invoked both ways:
  - python main.py <command>
  - python -m main <command>
"""

import sys
from pathlib import Path
from main import app

# Add src directory to Python path when running as a module
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

if __name__ == "__main__":
    app()
