"""
CLI command definitions for nxtool."""

import argparse
import sys

from core.builder import build
from core.flasher import flash
from core.config import configure
from core.terminal import terminal


def create_parser() -> argparse.ArgumentParser:
    """
    Create the main argument parser for nxtool.

        Returns:
            argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Unified CLI tool for NuttX board development tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build NuttX project")
    build_parser.add_argument("nuttx_path", help="Path to NuttX directory")
    build_parser.add_argument("--target", help="Build target (default: all)")
    build_parser.add_argument(
        "--jobs", "-j", type=int, help="Number of parallel jobs for Make build"
    )

    # Configure command
    config_parser = subparsers.add_parser("configure", help="Configure NuttX project")
    config_parser.add_argument("board_config", help="Board configuration string")
    config_parser.add_argument("nuttx_path", help="Path to NuttX directory")
    config_parser.add_argument(
        "--preset", action="append", help="Apply preset configuration"
    )
    config_parser.add_argument(
        "--cmake", action="store_true", help="Use CMake for configuration"
    )

    # Flash command
    flash_parser = subparsers.add_parser("flash", help="Flash firmware to board")
    flash_parser.add_argument("nuttx_path", help="Path to NuttX directory")
    flash_parser.add_argument("--port", help="Serial port (for ESP32 targets)")
    flash_parser.add_argument(
        "--openocd", help="Path to OpenOCD executable (for STM32 targets)"
    )

    # Terminal command
    term_parser = subparsers.add_parser("term", help="Open serial terminal")
    term_parser.add_argument("nuttx_path", help="Path to NuttX directory")
    term_parser.add_argument("--port", help="Specific serial port to use")
    term_parser.add_argument(
        "--python", default=sys.executable, help="Python executable to use"
    )

    return parser


def handle_build(args) -> None:
    """
    Handle build command.

        Args:
            args: Parsed command line arguments
    """
    build(args.nuttx_path, args.target, args.jobs)


def handle_configure(args) -> None:
    """
    Handle configure command.

        Args:
            args: Parsed command line arguments
    """
    configure(
        args.board_config,
        args.nuttx_path,
        args.preset,
        args.cmake,
    )


def handle_flash(args) -> None:
    """
    Handle flash command.

        Args:
            args: Parsed command line arguments
    """
    flash(args.nuttx_path, args.port, args.openocd)


def handle_terminal(args) -> None:
    """
    Handle terminal command.

        Args:
            args: Parsed command line arguments
    """
    terminal(args.nuttx_path, args.port, args.python)


def main() -> None:
    """
    Main entry point for CLI commands."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Command handlers
    handlers = {
        "build": handle_build,
        "configure": handle_configure,
        "flash": handle_flash,
        "term": handle_terminal,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)
