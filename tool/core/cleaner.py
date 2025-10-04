"""
Clean functionality for NuttX projects."""

import os
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
    # Check for .config file - if it exists, it's a make-based system
    config_file = os.path.join(nuttx_path, ".config")
    if os.path.exists(config_file):
        print("Detected Make build system (.config exists)")
        return "make"

    # Otherwise, assume it's a cmake-based system with build directory at same level
    print("Detected CMake build system (.config not found)")
    return "cmake"


def clean_with_make(nuttx_path: str) -> None:
    """
    Clean NuttX using Make.

        Args:
            nuttx_path(str): Path to NuttX directory
    """
    os.chdir(nuttx_path)
    run_command("make clean")


def clean_with_cmake(nuttx_path: str) -> bool:
    """
    Clean NuttX using CMake.

        Args:
            nuttx_path(str): Path to NuttX directory

        Returns:
            bool: True if successful, False if failed
    """
    # Get parent directory of NuttX
    parent_dir = os.path.dirname(nuttx_path)
    build_dir = os.path.join(parent_dir, "build")

    if not os.path.exists(build_dir):
        print("Error: Build directory not found. Nothing to clean.")
        return False

    os.chdir(build_dir)
    run_command("ninja clean")
    return True


def clean(nuttx_path: str) -> bool:
    """
    Clean NuttX project with auto-detected build system.

        Args:
            nuttx_path: Path to NuttX directory

        Returns:
            bool: True if successful, False if failed
    """
    nuttx_path = validate_path(nuttx_path)

    build_system = detect_build_system(nuttx_path)

    print(f"Cleaning NuttX using {build_system}...")

    if build_system == "make":
        clean_with_make(nuttx_path)
    else:
        if not clean_with_cmake(nuttx_path):
            return False

    print("Clean completed successfully!")
    return True


def rebuild_with_make(nuttx_path: str, jobs: Optional[int] = None) -> None:
    """
    Rebuild NuttX using Make with bear to generate compile_commands.json.

        Args:
            nuttx_path(str): Path to NuttX directory
            jobs(int): Number of parallel jobs (default: CPU count)
    """
    import multiprocessing

    # Get the current working directory (Python launch directory)
    launch_dir = os.getcwd()

    if jobs is None:
        jobs = multiprocessing.cpu_count()
        print(f"Using {jobs} parallel jobs (CPU count)")

    # Use bear to generate compile_commands.json at launch directory while building in nuttx directory
    run_command(
        f"bear --output {launch_dir}/compile_commands.json -- make -C {nuttx_path} -j{jobs}"
    )


def rebuild(nuttx_path: str, jobs: Optional[int] = None) -> bool:
    """
    Rebuild NuttX project with bear to generate compile_commands.json (make-based only).

        Args:
            nuttx_path: Path to NuttX directory
            jobs: Number of parallel jobs for Make build (default: CPU count)

        Returns:
            bool: True if successful, False if failed
    """
    nuttx_path = validate_path(nuttx_path)

    build_system = detect_build_system(nuttx_path)

    if build_system != "make":
        print("Error: rebuild command only supports make-based build systems")
        print(
            "For cmake-based systems, compile_commands.json is generated automatically during configuration"
        )
        return False

    print(f"Rebuilding NuttX using {build_system} with bear...")

    if jobs:
        print(f"Using {jobs} parallel jobs")
    rebuild_with_make(nuttx_path, jobs)

    print("Rebuild completed successfully! compile_commands.json generated.")
    return True
