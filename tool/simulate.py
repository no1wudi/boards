#!/usr/bin/env python3
import os
import subprocess
import sys
from kconfig import Kconfig

# Mapping of target detection rules to QEMU commands
TARGET_CONFIGS = {
    # Format: {target_name: {'required': [configs], 'optional': [configs], 'command': qemu_cmd, 'file_ext': file_extension}}
    "qemu-rv32": {
        "required": ["CONFIG_ARCH_BOARD_QEMU_RV_VIRT=y", "CONFIG_ARCH_RV32=y"],
        "command": "qemu-system-riscv32 -semihosting -M virt,aclint=on -cpu rv32 -smp 8 -bios none -kernel {kernel_path} -nographic",
    },
    "qemu-rv64": {
        "required": ["CONFIG_ARCH_BOARD_QEMU_RV_VIRT=y", "CONFIG_ARCH_RV64=y"],
        "command": "qemu-system-riscv64 -semihosting -M virt,aclint=on -cpu rv64 -smp 8 -bios none -kernel {kernel_path} -nographic",
    },
    "sabre-6quad": {
        "required": ["CONFIG_ARCH_CHIP_IMX6_6QUAD=y", "CONFIG_SMP is not set"],
        "command": "qemu-system-arm -M sabrelite -smp 1 -kernel {kernel_path} -nographic",
    },
    "sabre-6quad-smp": {
        "required": ["CONFIG_ARCH_CHIP_IMX6_6QUAD=y", "CONFIG_SMP=y"],
        "command": "qemu-system-arm -M sabrelite -smp 4 -kernel {kernel_path} -nographic",
    },
    "mps3-an547": {
        "required": ["CONFIG_ARCH_BOARD_MPS3_AN547=y"],
        "command": "qemu-system-arm -M mps3-an547 -kernel {kernel_path} -nographic",
    },
    "qemu-i486": {
        "required": ["CONFIG_ARCH_CHIP_QEMU_I486=y"],
        "command": "qemu-system-i386 -kernel {kernel_path} -nographic",
        "file_ext": ".elf",
    },
    "qemu-x64": {
        "required": ["CONFIG_ARCH_BOARD_INTEL64_QEMU=y"],
        "command": "qemu-system-x86_64 -cpu host --enable-kvm -m 2G -kernel {kernel_path} -nographic",
    },
    "sim": {
        "required": ["CONFIG_ARCH_SIM=y", "CONFIG_HOST_X86_64=y"],
        "command": "{kernel_path}",
    },
}


def detect_target(nuttx_path):
    """
    Detect target architecture from NuttX .config file.

    Args:
        nuttx_path (str): Path to NuttX build directory containing .config

    Returns:
        str: Name of detected target (e.g., 'qemu-rv32') or None if no match found

    Raises:
        SystemExit: If .config file is not found
    """
    config_path = os.path.join(nuttx_path, ".config")

    try:
        kconfig = Kconfig(config_path)
    except FileNotFoundError:
        print(f"Error: .config file not found in {nuttx_path}")
        sys.exit(1)

    # Check each target configuration
    for target_name, target_config in TARGET_CONFIGS.items():
        if kconfig.check_configs(target_config["required"]):
            return target_name
    return None


def run_simulation(nuttx_path):
    """
    Run QEMU simulation based on detected target architecture.

    Args:
        nuttx_path (str): Path to NuttX build directory containing nuttx binary

    Raises:
        SystemExit: If target cannot be detected or simulation fails
    """
    target = detect_target(nuttx_path)

    if not target:
        print("Error: Could not detect target architecture from .config")
        sys.exit(1)

    kernel_path = os.path.join(nuttx_path, "nuttx")
    file_ext = ""
    if "file_ext" in TARGET_CONFIGS[target]:
        file_ext = TARGET_CONFIGS[target]["file_ext"]

    cmd = TARGET_CONFIGS[target]["command"].format(
        kernel_path=f"{kernel_path}{file_ext}"
    )
    print(f"Target: {target}")
    print(f"Running: {cmd}")

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Simulation failed: {e}")
        sys.exit(1)


def main():
    """
    Main entry point for the simulation tool.

    Parses command line arguments and initiates simulation.

    Usage:
        simulate.py <path_to_nuttx>

    Raises:
        SystemExit: If incorrect number of arguments provided
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_nuttx>")
        sys.exit(1)

    nuttx_path = os.path.abspath(sys.argv[1])
    run_simulation(nuttx_path)


if __name__ == "__main__":
    main()
