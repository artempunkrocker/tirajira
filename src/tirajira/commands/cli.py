"""
CLI interface for TiraJira.
"""

import argparse
import sys

from .. import __version__
from .extract_failed import ExtractFailedCommand
from .import_cmd import ImportCommand
from .resume import ResumeCommand


def create_argument_parser():
    """Creates a command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="tirajira",
        description="Tool for automating mass task creation in Jira",
    )

    # Add common arguments
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for import command
    import_parser = subparsers.add_parser(
        "import", help="Import and create tasks from file"
    )
    import_parser.add_argument("file", help="Path to the task file")
    import_parser.add_argument(
        "--max-concurrent-requests",
        "-mcr",
        type=int,
        default=10,
        help="Maximum number of concurrent requests (default: 10)",
    )
    import_parser.add_argument(
        "--min-request-interval",
        "-mri",
        type=float,
        default=1.0,
        help="Minimum interval between requests in seconds (default: 1.0)",
    )
    import_parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop processing on error",
    )
    import_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging mode",
    )
    import_parser.add_argument(
        "--report",
        nargs="?",
        const=True,
        help="Save machine-readable execution report in JSON, "
        "CSV, Excel, or YAML format",
    )

    # Subparser for extract-failed command
    extract_failed_parser = subparsers.add_parser(
        "extract-failed", help="Extract failed tasks from report"
    )
    extract_failed_parser.add_argument("report_file", help="Path to the report file")
    extract_failed_parser.add_argument("output_file", help="Path to the output file")

    # Subparser for resume command
    resume_parser = subparsers.add_parser(
        "resume", help="Continue execution from report"
    )
    resume_parser.add_argument("report_file", help="Path to the report file")
    resume_parser.add_argument(
        "--max-concurrent-requests",
        "-mcr",
        type=int,
        default=10,
        help="Maximum number of concurrent requests (default: 10)",
    )
    resume_parser.add_argument(
        "--min-request-interval",
        "-mri",
        type=float,
        default=1.0,
        help="Minimum interval between requests in seconds (default: 1.0)",
    )
    resume_parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop processing on error",
    )
    resume_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging mode",
    )
    resume_parser.add_argument(
        "--report",
        nargs="?",
        const=True,
        help="Save machine-readable execution report in JSON, "
        "CSV, Excel, or YAML format",
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.command == "import":
        command = ImportCommand(args)
        result = command.run()
        if result == 1:
            sys.exit(1)
    elif args.command == "extract-failed":
        command = ExtractFailedCommand(args)
        result = command.run()
        if result == 1:
            sys.exit(1)
    elif args.command == "resume":
        command = ResumeCommand(args)
        result = command.run()
        if result == 1:
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
