"""
Module for displaying help information for the TiraJira utility.
"""

from .. import __version__


def display_help() -> None:
    """Displays help information for the utility."""
    help_text = f"""
TiraJira - tool for automating mass task creation in Jira.

Description:
  Utility allows creating tasks in Jira from JSON, YAML, CSV, or Excel files.
  Supports linking tasks to epics and logging the task creation process.

Supported file formats:
  - JSON (.json)
  - YAML (.yaml, .yml)
  - CSV (.csv)
  - Excel (.xlsx)

Usage:
  python3 main.py <path_to_file>
  python3 main.py --help
  python3 main.py --version

Examples:
  # Create tasks from JSON file
  python3 main.py tasks.json

  # Create tasks from YAML file
  python3 main.py tasks.yaml

  # Create tasks from CSV file
  python3 main.py tasks.csv

  # Create tasks from Excel file
  python3 main.py tasks.xlsx

  # Display help
  python3 main.py --help

  # Display version
  python3 main.py --version

Version: {__version__}

Additional information:
  Before using, you need to configure Jira connection parameters in the .env file
  Copy .env.example to .env and fill in your data.
"""
    print(help_text)
