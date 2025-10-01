"""
Build functionality for NuttX projects."""

import os
import sys
from typing import Optional

from utils.helpers import run_command, validate_path


def detect_build_system(nuttx_path: str) -> str:
    """
    Detect the build system used by the NuttX project.

        Args:
            nuttx_path(str): Path to NuttX directory

        Returns:
            str: Either 'make' or 'cmake'
    """
    # Check for .config file - if it exists, it's a make - based system
    config_file = os.path.join(nuttx_path, ".config")
    if os.path.exists(config_file):
        print("Detected Make build system (.config exists)")
        return "make"

    # Otherwise, assume it's a cmake - based system with build directory at same level
    print("Detected CMake build system (.config not found)")
    return "cmake"


def build_with_make(nuttx_path: str, target: str = "all") -> None:
    """
    Build NuttX using Make.

        Args:
            nuttx_path(str): Path to NuttX directory
            target(str): Make target to build(default: 'all')
    """
    os.chdir(nuttx_path)
    run_command(f"make {target}")


def build_with_cmake(nuttx_path: str, target: str = "all") -> None:
    """
    Build NuttX using CMake.

        Args:
            nuttx_path(str): Path to NuttX directory
            target(str): CMake target to build(default: 'all')
    """
    # Get parent directory of NuttX
    parent_dir = os.path.dirname(nuttx_path)
    build_dir = os.path.join(parent_dir, "build")

    if not os.path.exists(build_dir):
        print("Error: Build directory not found. Run configure first.")
        sys.exit(1)

    os.chdir(build_dir)
    run_command(f"ninja {target}")


def build(nuttx_path: str, target: Optional[str] = None) -> None:
    """
    Build NuttX project with auto - detected build system.

        Args:
            nuttx_path: Path to NuttX directory
            target: Build target(default: 'all')
    """
    nuttx_path = validate_path(nuttx_path)

    if target is None:
        target = "all"

    build_system = detect_build_system(nuttx_path)

    print(f"Building NuttX using {build_system}...")

    if build_system == "make":
        build_with_make(nuttx_path, target)
    else:
        build_with_cmake(nuttx_path, target)

    print("Build completed successfully!")
