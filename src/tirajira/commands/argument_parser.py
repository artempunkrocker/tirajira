"""
Module for parsing command line arguments.
"""

import argparse
import sys

from .. import __version__
from .help_manager import display_help


class ArgumentParser:
    """Class for parsing command line arguments."""

    def __init__(self) -> None:
        """Initializes the argument parser."""
        self.parser = argparse.ArgumentParser(
            description="TiraJira - tool for automating task creation in Jira",
            add_help=False,
        )
        self._add_arguments()

    def _add_arguments(self) -> None:
        """Adds arguments to the parser."""
        self.parser.add_argument("file_path", nargs="?", help="Path to the task file")
        self.parser.add_argument(
            "--max-concurrent-requests",
            "-mcr",
            type=int,
            default=10,
            help="Maximum number of concurrent requests (default: 10)",
        )
        self.parser.add_argument(
            "--min-request-interval",
            "-mri",
            type=float,
            default=1.0,
            help="Minimum interval between requests in seconds (default: 1.0)",
        )
        self.parser.add_argument(
            "--stop-on-error",
            action="store_true",
            help="Stop processing on error",
        )
        self.parser.add_argument(
            "--verbose", action="store_true", help="Enable verbose output mode"
        )
        self.parser.add_argument(
            "--report",
            nargs="?",
            const=True,
            default=None,
            help="Save execution report (if specified without value, "
            "filename is generated automatically)",
        )
        self.parser.add_argument("--help", "-h", action="store_true", help="Show help")
        self.parser.add_argument("--version", action="store_true", help="Show version")

    def parse(self) -> argparse.Namespace:
        """
        Parses command line arguments.

        Returns:
            Namespace with parsed arguments.
        """
        return self.parser.parse_args()

    def handle_special_args(self, args: argparse.Namespace) -> bool:
        """
        Handles special arguments (--help, --version).

        Args:
            args: Parsed arguments.

        Returns:
            True if a special command (help or version) was executed,
            otherwise False.
        """
        if args.version:
            print(f"TiraJira version {__version__}")
            return True

        if args.help or (len(sys.argv) == 1 and not args.file_path):
            display_help()
            return True

        return False

    def validate_args(self, args: argparse.Namespace) -> bool:
        """
        Validates arguments.

        Args:
            args: Parsed arguments.

        Returns:
            True if arguments are valid, otherwise False.
        """
        if not args.file_path:
            print("Error: No path to task file specified")
            display_help()
            return False
        return True
