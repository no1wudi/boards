import serial.tools.list_ports
import argparse


def parse_args():
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments containing the target device.
    """
    parser = argparse.ArgumentParser(
        description="Find serial port for specific devices"
    )
    parser.add_argument(
        "target",
        type=str,
        help="Target device to search for",
    )
    return parser.parse_args()


def find_device_port(target):
    """Find the serial port for a specific device.

    Args:
        target (str): The target device to search for (esp32c3, esp32s3, or stlink).

    Returns:
        str or None: Device port path if found, None otherwise.
    """
    # VID:PID combinations
    DEVICE_IDS = {
        "esp32s3": [
            "303A:1001",  # USB Serial-JTAG
        ],
        "stm32f746g-disco": [
            "0483:374B",  # ST-Link V2-1
        ]
    }

    if target not in DEVICE_IDS:
        print(f"Error: Unsupported target: {target}")
        return None

    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("Error: No serial ports found")
        return None

    for port in ports:
        # Skip ports without VID/PID
        if port.vid is None or port.pid is None:
            continue

        vid_pid = f"{port.vid:04X}:{port.pid:04X}"
        print(f"Found device: {port.device} ({vid_pid})")
        if vid_pid in DEVICE_IDS[target]:
            print(f"Found matching device at: {port.device}")
            return port.device

    print(f"Error: No {target} device found")
    return None


def main():
    """Main entry point of the script.

    Returns:
        int: 0 if device port was found, 1 otherwise.
    """
    args = parse_args()
    find_device_port(args.target.lower())


if __name__ == "__main__":
    main()
