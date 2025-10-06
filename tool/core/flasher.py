"""Flashing functionality for NuttX boards."""

import os
import sys
from typing import Dict, Optional, Any
from utils.helpers import run_command, validate_path
from utils.kconfig import Kconfig

# Default OpenOCD path
DEFAULT_OPENOCD_PATH: str = "/mnt/d/Develop/openocd/bin/openocd.exe"

# Mapping of target flashing configurations
FLASH_CONFIGS: Dict[str, Dict[str, Any]] = {
    "esp32": {
        "required": ["CONFIG_ARCH_CHIP_ESP32=y"],
        "command": "esptool --chip auto --port {port} --baud 921600 write_flash 0x0 {firmware}",
        "filename": "nuttx.bin",
        "type": "esptool",
    },
    "esp32c3": {
        "required": ["CONFIG_ARCH_CHIP_ESP32C3=y"],
        "command": "esptool --chip auto --port {port} --baud 921600 write_flash 0x0 {firmware}",
        "filename": "nuttx.bin",
        "type": "esptool",
    },
    "esp32s3": {
        "required": ["CONFIG_ARCH_CHIP_ESP32S3=y"],
        "command": "esptool --chip auto --port {port} --baud 921600 write_flash 0x0 {firmware}",
        "filename": "nuttx.bin",
        "type": "esptool",
    },
    "stm32f746g-disco": {
        "required": ["CONFIG_ARCH_BOARD_STM32F746G_DISCO=y"],
        "command": '{openocd} -f interface/stlink.cfg -f target/stm32f7x.cfg -c "program {firmware} verify reset exit"',
        "filename": "nuttx.bin",
        "type": "openocd",
    },
}


def detect_target(nuttx_path: str) -> Optional[str]:
    """
    Detect target board from NuttX .config file.

        Args:
            nuttx_path(str): Path to NuttX directory

        Returns:
            str: Name of detected target or None if no match found
    """
    config_path = os.path.join(nuttx_path, ".config")

    try:
        kconfig = Kconfig(config_path)
    except FileNotFoundError:
        print(f"Error: .config file not found in {nuttx_path}")
        return None

    # Check each target configuration
    for target_name, target_config in FLASH_CONFIGS.items():
        if kconfig.check_configs(target_config["required"]):
            return target_name
    return None


def get_firmware_path(nuttx_path: str, filename: str) -> str:
    """
    Get the full path to the firmware file.

        Args:
            nuttx_path(str): Path to NuttX directory
            filename(str): Firmware filename

        Returns:
            str: Full path to firmware file

        Raises:
            SystemExit: If firmware file not found
    """
    # Check in nuttx directory first
    firmware_path = os.path.join(nuttx_path, filename)
    if os.path.exists(firmware_path):
        return firmware_path

    # Check in build directory for CMake builds
    parent_dir = os.path.dirname(nuttx_path)
    build_dir = os.path.join(parent_dir, "build")
    firmware_path = os.path.join(build_dir, filename)
    if os.path.exists(firmware_path):
        return firmware_path

    print(f"Error: Firmware file not found: {filename}")
    print("Searched in:")
    print(f"  {nuttx_path}")
    print(f"  {build_dir}")
    sys.exit(1)


def flash_with_esptool(command: str, port: str, firmware: str) -> None:
    """
    Flash using esptool.

        Args:
            command(str): Flash command template
            port(str): Serial port
            firmware(str): Firmware file path
    """
    cmd = command.format(port=port, firmware=firmware)
    print(f"Running: {cmd}")
    run_command(cmd)


def flash_with_openocd(command: str, openocd_path: str, firmware: str) -> None:
    """
    Flash using OpenOCD.

        Args:
            command(str): Flash command template
            openocd_path(str): Path to OpenOCD executable
            firmware(str): Firmware file path
    """
    cmd = command.format(openocd=openocd_path, firmware=firmware)
    print(f"Running: {cmd}")
    run_command(cmd)


def flash(
    nuttx_path: str,
    port: Optional[str] = None,
    openocd_path: Optional[str] = None,
) -> None:
    """
    Flash firmware to detected target board.

        Args:
            nuttx_path: Path to NuttX directory
            port: Serial port(for ESP32 targets)
            openocd_path: Path to OpenOCD executable(for STM32 targets)
    """
    nuttx_path = validate_path(nuttx_path)

    target = detect_target(nuttx_path)
    if not target:
        print("Error: Could not detect target board from .config")
        sys.exit(1)

    target_config = FLASH_CONFIGS[target]
    firmware_path = get_firmware_path(nuttx_path, target_config["filename"])

    print(f"Target: {target}")
    print(f"Firmware: {firmware_path}")

    if target_config["type"] == "esptool":
        if not port:
            print("Error: --port required for ESP32 targets")
            sys.exit(1)
        flash_with_esptool(target_config["command"], port, firmware_path)

    elif target_config["type"] == "openocd":
        if not openocd_path:
            openocd_path = DEFAULT_OPENOCD_PATH
        flash_with_openocd(target_config["command"], openocd_path, firmware_path)

    else:
        print(f"Error: Unknown flash type: {target_config['type']}")
        sys.exit(1)

    print("Flash completed successfully!")
