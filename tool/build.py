import os
import sys
import argparse
import subprocess


def run_command(cmd: str) -> None:
    """Execute a shell command and exit on failure.

    Args:
        cmd (str): The shell command to execute

    Raises:
        SystemExit: If the command fails (non-zero return code)
    """
    ret = subprocess.run(cmd, shell=True)
    if ret.returncode != 0:
        print(f"Error executing command: {cmd}")
        sys.exit(1)


def detect_build_system(nuttx_path: str) -> str:
    """Detect the build system used by the NuttX project.

    Args:
        nuttx_path (str): Path to NuttX directory

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


def build_with_make(nuttx_path: str, target: str = "all") -> None:
    """Build NuttX using Make.

    Args:
        nuttx_path (str): Path to NuttX directory
        target (str): Make target to build (default: 'all')
    """
    os.chdir(nuttx_path)

    # Check if NuttX is configured
    if not os.path.exists(os.path.join(nuttx_path, ".config")):
        print("Error: NuttX is not configured. Run configure first.")
        sys.exit(1)

    # Use multiple jobs for parallel build
    num_jobs = os.cpu_count() or 1
    print(f"Building with Make, target: {target}, jobs: {num_jobs}")
    run_command(f"make {target} -j{num_jobs}")


def build_with_cmake(nuttx_path: str) -> None:
    """Build NuttX using CMake.

    Args:
        nuttx_path (str): Path to NuttX directory
    """
    # Build directory is at same level as nuttx directory (../build)
    parent_dir = os.path.dirname(nuttx_path)
    build_dir = os.path.join(parent_dir, "build")

    if not os.path.exists(build_dir):
        print("Error: Build directory not found. Run configure first.")
        sys.exit(1)

    os.chdir(build_dir)

    # Check if build directory is configured
    if not os.path.exists(os.path.join(build_dir, "Makefile")) and not os.path.exists(
        os.path.join(build_dir, "build.ninja")
    ):
        print("Error: Build directory is not configured. Run configure first.")
        sys.exit(1)

    print("Building with CMake")
    run_command("cmake --build .")


def main() -> None:
    """Main entry point for NuttX build tool.

    Detects build system and builds with default target.
    """
    parser = argparse.ArgumentParser(
        description="Build NuttX using detected build system"
    )
    parser.add_argument("nuttx", help="Path to NuttX directory")
    args = parser.parse_args()

    # Convert paths to absolute
    NUTTX_PATH = os.path.abspath(args.nuttx)

    if not os.path.exists(NUTTX_PATH):
        print(f"NuttX path not found: {NUTTX_PATH}")
        sys.exit(1)

    # Determine build system
    try:
        build_system = detect_build_system(NUTTX_PATH)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Build the project with default target
    print(f"Detected build system: {build_system.upper()}")
    print("Building NuttX...")

    if build_system == "cmake":
        build_with_cmake(NUTTX_PATH)
    else:
        build_with_make(NUTTX_PATH, "all")

    print("Build completed successfully!")


if __name__ == "__main__":
    main()
