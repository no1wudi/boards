"""
CLI command definitions for nxtool.
"""

import argparse
import sys

from core.builder import build
from core.flasher import flash
from core.config import configure

from core.cleaner import clean, rebuild
from core.simulator import simulate


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

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean NuttX project")
    clean_parser.add_argument("nuttx_path", help="Path to NuttX directory")

    # Rebuild command
    rebuild_parser = subparsers.add_parser(
        "rebuild",
        help=(
            "Rebuild NuttX project with bear to generate compile_commands.json "
            "(make-based only)"
        ),
    )
    rebuild_parser.add_argument("nuttx_path", help="Path to NuttX directory")
    rebuild_parser.add_argument(
        "--jobs", "-j", type=int, help="Number of parallel jobs for Make build"
    )

    # Simulate command
    sim_parser = subparsers.add_parser("simulate", help="Run QEMU simulation")
    sim_parser.add_argument("nuttx_path", help="Path to NuttX directory")
    sim_parser.add_argument(
        "--qemu-options",
        help="Additional options to pass to QEMU (e.g., '-S -s' for debug)",
    )

    return parser


def handle_build(args: argparse.Namespace) -> None:
    """
    Handle build command.

    Args:
        args: Parsed command line arguments
    """
    if not args.nuttx_path:
        print("Error: nuttx_path is required")
        sys.exit(1)

    try:
        build(args.nuttx_path, args.target, args.jobs)
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)


def handle_configure(args: argparse.Namespace) -> None:
    """
    Handle configure command.

    Args:
        args: Parsed command line arguments
    """
    if not args.board_config:
        print("Error: board_config is required")
        sys.exit(1)
    if not args.nuttx_path:
        print("Error: nuttx_path is required")
        sys.exit(1)

    try:
        configure(
            args.board_config,
            args.nuttx_path,
            args.preset,
            args.cmake,
        )
    except Exception as e:
        print(f"Configuration failed: {e}")
        sys.exit(1)


def handle_flash(args: argparse.Namespace) -> None:
    """
    Handle flash command.

    Args:
        args: Parsed command line arguments
    """
    if not args.nuttx_path:
        print("Error: nuttx_path is required")
        sys.exit(1)

    try:
        flash(args.nuttx_path, args.port, args.openocd)
    except Exception as e:
        print(f"Flash failed: {e}")
        sys.exit(1)


def handle_clean(args: argparse.Namespace) -> None:
    """
    Handle clean command.

    Args:
        args: Parsed command line arguments
    """
    if not args.nuttx_path:
        print("Error: nuttx_path is required")
        sys.exit(1)

    try:
        if not clean(args.nuttx_path):
            print("Clean operation failed")
            sys.exit(1)
    except Exception as e:
        print(f"Clean failed: {e}")
        sys.exit(1)


def handle_rebuild(args: argparse.Namespace) -> None:
    """
    Handle rebuild command.

    Args:
        args: Parsed command line arguments
    """
    if not args.nuttx_path:
        print("Error: nuttx_path is required")
        sys.exit(1)

    try:
        if not rebuild(args.nuttx_path, args.jobs):
            print("Rebuild operation failed")
            sys.exit(1)
    except Exception as e:
        print(f"Rebuild failed: {e}")
        sys.exit(1)


def handle_simulate(args: argparse.Namespace) -> None:
    """
    Handle simulate command.

    Args:
        args: Parsed command line arguments
    """
    if not args.nuttx_path:
        print("Error: nuttx_path is required")
        sys.exit(1)

    try:
        simulate(args.nuttx_path, args.qemu_options)
    except Exception as e:
        print(f"Simulation failed: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main entry point for CLI commands.

    This function parses command line arguments and dispatches to the appropriate
    command handler. It provides consistent error handling and user feedback.
    """
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Command handlers mapping
    handlers = {
        "build": handle_build,
        "configure": handle_configure,
        "flash": handle_flash,
        "clean": handle_clean,
        "rebuild": handle_rebuild,
        "simulate": handle_simulate,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)
