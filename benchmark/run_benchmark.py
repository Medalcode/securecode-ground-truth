"""Command-line entry point to execute the SecureCode Ground Truth benchmark."""

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmark.runner import main

if __name__ == "__main__":
    main()
