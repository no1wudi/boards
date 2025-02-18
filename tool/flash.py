#!/usr/bin/env python3
import os
import subprocess
import sys
import argparse
from kconfig import Kconfig

# Mapping of target flashing configurations
FLASH_CONFIGS = {
    "esp32": {
        "required": ["CONFIG_ARCH_CHIP_ESP32=y"],
        "command": "-m esptool --chip auto --baud 921600 write_flash 0x0 {firmware}",
        "filename": "nuttx.bin"
    },
    "esp32c3": {
        "required": ["CONFIG_ARCH_CHIP_ESP32C3=y"],
        "command": "-m esptool --chip auto --baud 921600 write_flash 0x0 {firmware}",
        "filename": "nuttx.bin"
    },
    "esp32s3": {
        "required": ["CONFIG_ARCH_CHIP_ESP32S3=y"],
        "command": "-m esptool --chip auto --baud 921600 write_flash 0x0 {firmware}",
        "filename": "nuttx.bin"
    }
}


def detect_target(nuttx_path):
    """
    Detect target from NuttX .config file.
    """
    config_path = os.path.join(nuttx_path, ".config")

    try:
        kconfig = Kconfig(config_path)
    except FileNotFoundError:
        print(f"Error: .config file not found in {nuttx_path}")
        sys.exit(1)

    for target_name, target_config in FLASH_CONFIGS.items():
        if kconfig.check_configs(target_config["required"]):
            return target_name
    return None


def flash_firmware(nuttx_path, port=None, python_exec=None):
    """
    Flash firmware based on detected target.
    """
    target = detect_target(nuttx_path)
    if not target:
        print("Error: Could not detect supported target from .config")
        sys.exit(1)

    if target not in FLASH_CONFIGS:
        print(f"Error: Flashing not yet implemented for {target}")
        sys.exit(1)

    if port is None:
        print("Error: Serial port must be specified")
        sys.exit(1)

    config = FLASH_CONFIGS[target]
    firmware_path = os.path.join(nuttx_path, config["filename"])

    if not os.path.exists(firmware_path):
        print(f"Error: Firmware not found at {firmware_path}")
        sys.exit(1)

    # Prepend Python executable to command if specified
    base_cmd = config["command"]
    if python_exec:
        base_cmd = f"{python_exec} {base_cmd}"

    cmd = base_cmd.format(port=port, firmware=firmware_path)
    print(f"Target: {target}")
    print(f"Running: {cmd}")

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Flashing failed: {e}")
        sys.exit(1)


def main():
    """
    Main entry point for the flashing tool.
    """
    parser = argparse.ArgumentParser(description="Firmware flashing tool")
    parser.add_argument("nuttx_path", help="Path to NuttX build directory")
    parser.add_argument("--port", "-p", help="Serial port for flashing", required=True)
    parser.add_argument(
        "--python",
        help="Python executable to use (e.g., python3)",
        default=sys.executable,
    )

    args = parser.parse_args()
    flash_firmware(args.nuttx_path, args.port, args.python)


if __name__ == "__main__":
    main()
