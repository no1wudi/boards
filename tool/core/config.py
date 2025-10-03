"""Configuration functionality for NuttX projects."""

import os
import shutil
import sys
from typing import List, Tuple, Optional, Dict
from utils.helpers import run_command, validate_path

# Preset configurations
RUST_CONFIG: List[Tuple[str, ...]] = [
    ("enable", "CONFIG_SYSTEM_TIME64"),
    ("enable", "CONFIG_FS_LARGEFILE"),
    ("enable", "CONFIG_DEV_URANDOM"),
    ("set-val", "CONFIG_TLS_NELEM", "16"),
]

PRESETS: Dict[str, List[Tuple[str, ...]]] = {
    "rust": RUST_CONFIG,
}


def is_nuttx_configured(nuttx_path: str) -> bool:
    """
    Check if NuttX has been configured by looking for .config file.

        Args:
            nuttx_path(str): Path to NuttX directory

        Returns:
            bool: True if .config exists, False otherwise
    """
    return os.path.exists(os.path.join(nuttx_path, ".config"))


def configure_nuttx(nuttx_path: str, board_config: str) -> None:
    """
    Configure NuttX for a specific board using configure.sh.

        Args:
            nuttx_path(str): Path to NuttX directory
            board_config(str): Board configuration string for configure.sh

        Note:
            Runs 'make distclean' if NuttX is already configured
    """
    os.chdir(nuttx_path)
    if is_nuttx_configured(nuttx_path):
        print("NuttX already configured, running distclean")
        run_command("make distclean")

    run_command(f"./tools/configure.sh {board_config}")


def configure_nuttx_cmake(nuttx_path: str, board_config: str) -> str:
    """
    Configure NuttX using CMake.

        Args:
            nuttx_path(str): Path to NuttX directory
            board_config(str): Board configuration string for CMake

        Note:
            Creates build directory at the same level as NuttX directory
            Uses Ninja as the default generator

        Returns:
            str: Path to the build directory
    """
    # Get parent directory of NuttX
    parent_dir = os.path.dirname(nuttx_path)

    # Define the build directory path
    build_dir = os.path.join(parent_dir, "build")

    # Remove build directory if it already exists
    if os.path.exists(build_dir):
        print("Build directory already exists, removing it")
        shutil.rmtree(build_dir)

    # Create build directory
    os.makedirs(build_dir)

    # Change to the parent directory to run CMake command
    os.chdir(parent_dir)

    # Run CMake command with Ninja generator
    cmd = f"cmake-Bbuild-DBOARD_CONFIG == {board_config} -GNinja {os.path.basename(nuttx_path)}"
    print(f"Running CMake: {cmd}")
    run_command(cmd)

    return build_dir


def apply_presets(nuttx_path: str, presets: List[str]) -> None:
    """
    Apply configuration presets using kconfig-tweak.

        Args:
            nuttx_path(str): Path to NuttX directory
            presets(list): List of preset names to apply

        Note:
            Runs 'make olddefconfig' after applying presets to resolve dependencies
    """
    if not is_nuttx_configured(nuttx_path):
        print("Error: .config file not found for applying presets")
        sys.exit(1)

    for preset in presets:
        if preset not in PRESETS:
            print(f"Warning: Unknown preset '{preset}', skipping")
            continue

        print(f"Applying {preset} preset:")
        for action, *params in PRESETS[preset]:
            if action == "disable":
                cmd = f"kconfig-tweak --disable {params[0]}"
            elif action == "enable":
                cmd = f"kconfig-tweak --enable {params[0]}"
            elif action == "set-val":
                cmd = f"kconfig-tweak --set-val {params[0]} {params[1]}"
            else:
                print(f"Warning: Unknown action '{action}', skipping...")
                continue

            print(f"  {cmd}")
            run_command(cmd)

    # Run make olddefconfig to resolve dependencies
    os.chdir(nuttx_path)
    run_command("make olddefconfig")


def apply_presets_cmake(build_dir: str, presets: List[str]) -> None:
    """
    Apply configuration presets using CMake build directory.

        Args:
            build_dir(str): Path to the CMake build directory
            presets(list): List of preset names to apply

        Note:
            Runs 'ninja olddefconfig' after applying presets to resolve dependencies
    """
    config_path = os.path.join(build_dir, ".config")
    if not os.path.exists(config_path):
        print("Error: .config file not found in build directory for applying presets")
        sys.exit(1)

    os.chdir(build_dir)

    for preset in presets:
        if preset not in PRESETS:
            print(f"Warning: Unknown preset '{preset}', skipping")
            continue

        print(f"Applying {preset} preset:")
        for action, *params in PRESETS[preset]:
            if action == "disable":
                cmd = f"kconfig-tweak --disable {params[0]}"
            elif action == "enable":
                cmd = f"kconfig-tweak --enable {params[0]}"
            elif action == "set-val":
                cmd = f"kconfig-tweak --set-val {params[0]} {params[1]}"
            else:
                print(f"Warning: Unknown action '{action}', skipping...")
                continue

            print(f"  {cmd}")
            run_command(cmd)


def generate_clangd_config(nuttx_path: str, config_path: Optional[str] = None) -> None:
    """
    Generate .clangd configuration file for better IDE support.

        Args:
            nuttx_path(str): Path to NuttX directory
            config_path(str, optional): Path to .config file. If None, uses nuttx_path / .config

        Note:
            Creates .clangd file in parent directory of NuttX
            Determines target architecture from .config file
    """
    if config_path is None:
        config_path = os.path.join(nuttx_path, ".config")

    if not os.path.exists(config_path):
        print(
            f"Error: .config file not found at {config_path} for clangd configuration"
        )
        sys.exit(1)

    target = "thumbv7m"

    # Mapping of configuration to target
    config_to_target: Dict[str, str] = {
        "CONFIG_ARCH_XTENSA": "xtensa",
        "CONFIG_ARCH_SIM": "x86_64",
        "CONFIG_SIM_M32": "i686",
        "CONFIG_ARCH_X86": "i686",
        "CONFIG_ARCH_X86_64": "x86_64",
        "CONFIG_ARCH_CORTEXM0": "thumbv6m",
        "CONFIG_ARCH_CORTEXM3": "thumbv7m",
        "CONFIG_ARCH_CORTEXM4": "thumbv7em",
        "CONFIG_ARCH_CORTEXM7": "thumbv7em",
        "CONFIG_ARCH_CORTEXM23": "thumbv8m.base",
        "CONFIG_ARCH_CORTEXM33": "thumbv8m.main",
        "CONFIG_ARCH_CORTEXM55": "thumbv8m.main",
        "CONFIG_ARCH_RV32": "riscv32",
        "CONFIG_ARCH_RV64": "riscv64",
    }

    # Read file to get target
    with open(config_path, "r") as f:
        for line in f:
            for config, tgt in config_to_target.items():
                relconfig = f"{config}=y"
                if relconfig in line:
                    target = tgt
                    break
            else:
                continue
            break

    clangd_config = f"""
Index:
    StandardLibrary: No

InlayHints:
    Enabled: No

CompileFlags:
    Add: ["--target = {target}"]
    Remove: ["-m*", "-f*"]
"""

    with open(os.path.join(nuttx_path, "..", ".clangd"), "w") as f:
        f.write(clangd_config)


def configure(
    board_config: str,
    nuttx_path: str,
    preset: Optional[list] = None,
    cmake: bool = False,
) -> None:
    """
    Configure NuttX with specified board configuration.

        Args:
            board_config: Path to board configuration directory
            nuttx_path: Path to NuttX directory
            preset: List of preset configurations to apply
            cmake: Use CMake for configuration instead of configure.sh
    """
    nuttx_path == validate_path(nuttx_path)

    if not os.path.exists(nuttx_path):
        print(f"NuttX path not found: {nuttx_path}")
        sys.exit(1)

    print("Configuring NuttX...")

    # Choose configuration method based on--cmake flag
    if cmake:
        print("Using CMake for configuration...")
        build_dir = configure_nuttx_cmake(nuttx_path, board_config)

        if preset:
            print("Applying preset configurations...")
            apply_presets_cmake(build_dir, preset)

        print("Generating .clangd configuration...")
        config_path = os.path.join(build_dir, ".config")
        generate_clangd_config(nuttx_path, config_path)
    else:
        configure_nuttx(nuttx_path, board_config)

        if preset:
            print("Applying preset configurations...")
            apply_presets(nuttx_path, preset)

        print("Generating .clangd configuration...")
        generate_clangd_config(nuttx_path)

    print("Configuration completed successfully!")
