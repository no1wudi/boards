#!/usr/bin/env python3

import sys
import os
import argparse
import subprocess
from kconfig import Kconfig

# Add this mapping at module level
TARGET_CONFIG_MAP = {
    "esp32c3": ["CONFIG_ARCH_CHIP_ESP32C3=y"],
    "esp32s3": ["CONFIG_ARCH_CHIP_ESP32S3=y"],
    "stm32f746g-disco": ["CONFIG_ARCH_BOARD_STM32F746G_DISCO=y"],
}

# Add this map after TARGET_CONFIG_MAP
BAUDRATE_CONFIG_MAP = {
    "esp32s3": {
        "configs": ["CONFIG_OTHER_SERIAL_CONSOLE=y", "CONFIG_ESP32S3_USBSERIAL=y"],
        "baudrate": 2000000,
    },
    "stm32f746g-disco": {
        "configs": ["CONFIG_ARCH_BOARD_STM32F746G_DISCO=y"],
        "baudrate": 115200,
    },
}


def get_device_port(python_exe, target):
    """
    Find the serial port for a specific target device.

    Args:
        python_exe (str): Path to Python interpreter
        target (str): Target device identifier (e.g., 'esp32c3', 'esp32s3')

    Returns:
        str or None: Device port path if found, None otherwise
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    getport_script = os.path.join(script_dir, "getport.py")

    try:
        # More efficient subprocess call
        output = subprocess.check_output(
            [python_exe, getport_script, target], text=True, stderr=subprocess.STDOUT
        ).strip()

        # Print the output for debugging purposes
        print(output)

        # More efficient parsing - search directly for the port information
        for line in output.splitlines():
            if "Found matching device at: " in line:
                return line.partition(": ")[2].strip()

    except subprocess.CalledProcessError as e:
        print(f"Warning: getport.py failed with exit code {e.returncode}")
        if e.output:
            print(f"Output: {e.output.strip()}")
    except FileNotFoundError:
        print(f"Warning: Could not find getport.py script at {getport_script}")
    except Exception as e:
        print(f"Warning: Failed to run getport.py: {e}")

    return None


def get_target_from_kconfig(nuttx_path):
    """
    Parse NuttX .config file to determine target device.

    Args:
        nuttx_path (str): Path to NuttX build directory containing .config

    Returns:
        str or None: Target identifier if found, None otherwise
    """
    config_path = os.path.join(nuttx_path, ".config")
    if not os.path.exists(config_path):
        print(f"Warning: Config file not found at {config_path}")
        return None

    # Early return if config file is empty
    if os.path.getsize(config_path) == 0:
        print(f"Warning: Config file is empty at {config_path}")
        return None

    try:
        kconfig = Kconfig(config_path)

        # Simple direct iteration through all targets
        for target, configs in TARGET_CONFIG_MAP.items():
            if kconfig.check_configs(configs):
                return target

    except FileNotFoundError:
        print(f"Error: Could not open config file {config_path}")
    except Exception as e:
        print(f"Warning: Failed to parse Kconfig: {str(e)}")

    return None


def get_baudrate_from_kconfig(nuttx_path, target):
    """
    Get serial baud rate from Kconfig settings.

    Args:
        nuttx_path (str): Path to NuttX build directory
        target (str): Target device identifier

    Returns:
        int: Baud rate value (default 115200 if invalid)
    """
    config_path = os.path.join(nuttx_path, ".config")
    if not os.path.exists(config_path):
        return 115200  # default fallback

    try:
        kconfig = Kconfig(config_path)

        if target in BAUDRATE_CONFIG_MAP:
            target_config = BAUDRATE_CONFIG_MAP[target]

            if "define" in target_config:
                defined_baud = kconfig.get_value(target_config["define"])
                try:
                    baud = int(defined_baud)
                    if baud > 0:
                        return baud
                except (ValueError, TypeError):
                    pass  # Invalid baudrate, fall through to predefined value

            if "baudrate" in target_config:
                return target_config["baudrate"]
            else:
                return 115200  # default fallback

    except Exception as e:
        print(f"Warning: Failed to get baud rate from Kconfig: {e}")

    return 115200  # default fallback


def main():
    """
    Main entry point for the serial terminal utility.

    Parses command line arguments, detects target device and port,
    and launches serial terminal with appropriate settings.
    """
    parser = argparse.ArgumentParser(
        description="Serial terminal with auto port detection"
    )
    parser.add_argument("nuttx_path", help="Path to NuttX build directory")
    parser.add_argument(
        "--port", "-p", help="Specific port to use (optional)", required=False
    )
    parser.add_argument(
        "--python",
        help="Python executable",
        default=sys.executable,
    )
    args = parser.parse_args()

    port = args.port
    target = get_target_from_kconfig(args.nuttx_path)
    if not port and target:
        port = get_device_port(args.python, target)

    if not port:
        print("Error: Could not determine port. Please specify --port")
        sys.exit(1)

    baudrate = get_baudrate_from_kconfig(args.nuttx_path, target)
    cmd = f"{args.python} -m serial.tools.miniterm --raw --eol CR {port} {baudrate}"
    os.system(cmd)


if __name__ == "__main__":
    main()
