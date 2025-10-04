"""Utility functions for the tool."""

import os
import subprocess
import sys


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


def run_command_with_output(cmd: str) -> str:
    """Execute a shell command and return output.

    Args:
        cmd (str): The shell command to execute

    Returns:
        str: Command output

    Raises:
        SystemExit: If the command fails (non-zero return code)
    """
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {cmd}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)


def validate_path(path: str, must_exist: bool = True) -> str:
    """Validate and return absolute path.

    Args:
        path (str): Path to validate
        must_exist (bool): Whether path must exist

    Returns:
        str: Absolute path

    Raises:
        SystemExit: If path validation fails
    """
    abs_path = os.path.abspath(path)
    if must_exist and not os.path.exists(abs_path):
        print(f"Error: Path does not exist: {abs_path}")
        sys.exit(1)
    return abs_path
