import os
import sys

# Calculate paths before importing
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")

# Add paths to sys.path for imports
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

from tirajira.logger import Logger  # noqa: E402

Logger.disable_console_output()
