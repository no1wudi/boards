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
        "command": "-m esptool --chip auto --port {port} --baud 921600 write_flash 0x0 {firmware}",
        "filename": "nuttx.bin",
        "type": "esptool",
    },
    "esp32c3": {
        "required": ["CONFIG_ARCH_CHIP_ESP32C3=y"],
        "command": "-m esptool --chip auto --port {port} --baud 921600 write_flash 0x0 {firmware}",
        "filename": "nuttx.bin",
        "type": "esptool",
    },
    "esp32s3": {
        "required": ["CONFIG_ARCH_CHIP_ESP32S3=y"],
        "command": "-m esptool --chip auto --port {port} --baud 921600 write_flash 0x0 {firmware}",
        "filename": "nuttx.bin",
        "type": "esptool",
    },
    "stm32f746g-disco": {
        "required": ["CONFIG_ARCH_BOARD_STM32F746G_DISCO=y"],
        "command": "openocd -f board/stm32f746g-disco.cfg -c \"program {firmware} verify reset exit 0x08000000\"",
        "filename": "nuttx.bin",
        "type": "openocd",
    },
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


def get_device_port(python_exe, target):
    """
    Find the serial port for a specific target device.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    getport_script = os.path.join(script_dir, "getport.py")

    try:
        result = subprocess.run(
            [python_exe, getport_script, target], capture_output=True, text=True
        )

        print(result.stdout.strip())
        for line in reversed(result.stdout.split("\n")):
            if "Found matching device at: " in line:
                return line.split(": ")[1]
    except Exception as e:
        print(f"Warning: Failed to run getport.py: {e}")

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

    config = FLASH_CONFIGS[target]
    # Only try to auto-detect port for targets with serial port type
    if port is None and config["type"] == "esptool":
        port = get_device_port(python_exec, target)
        if not port:
            print("Error: Could not auto-detect port. Please specify --port")
            sys.exit(1)
    elif port is None and config["type"] not in ["stlink", "openocd"]:
        print(f"Error: Port must be specified for {config['type']} type targets")
        sys.exit(1)

    firmware_path = os.path.join(nuttx_path, config["filename"])

    if not os.path.exists(firmware_path):
        print(f"Error: Firmware not found at {firmware_path}")
        sys.exit(1)

    # Prepend Python executable to command if specified and using Python-based tools
    base_cmd = config["command"]
    if python_exec and config["type"] == "esptool":
        base_cmd = f"{python_exec} {base_cmd}"

    cmd = base_cmd.format(target=target, port=port if port else "", firmware=firmware_path)
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
    parser.add_argument("--port", "-p", help="Port for flashing", required=False)
    parser.add_argument(
        "--python",
        help="Python executable to use (e.g., python3)",
        default=sys.executable,
    )

    args = parser.parse_args()
    flash_firmware(args.nuttx_path, args.port, args.python)


if __name__ == "__main__":
    main()
