"""Project configuration for imports."""

import sys
from pathlib import Path

# Add src directory to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
