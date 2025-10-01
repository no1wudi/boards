from typing import Optional

try:
    import serial.tools.list_ports

    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False


def find_device_port(target: str) -> Optional[str]:
    """
    Find the serial port for a specific device.

        Args:
            target(str): The target device to search for(esp32c3, esp32s3, or stlink).

        Returns:
            Optional[str]: The serial port path if found, None otherwise.
    """
    if not HAS_SERIAL:
        print("Error: pyserial module not found. Install with: pip install pyserial")
        return None

    ports = list(serial.tools.list_ports.comports())

    if not ports:
        print("Error: No serial ports found")
        return None

    for port in ports:
        port_name = port.device
        port_info = port.description or ""

        if target.lower() == "esp32c3":
            if "CP210" in port_info or "Silicon Labs" in port_info:
                return port_name
        elif target.lower() == "esp32s3":
            if "CP210" in port_info or "Silicon Labs" in port_info:
                return port_name
        elif target.lower() == "stlink":
            if "STLink" in port_info:
                return port_name

    return None

    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("Error: No serial ports found")
        return None

    for port in ports:
        # Skip ports without VID / PID
        if port.vid is None or port.pid is None:
            continue

        vid_pid = f"{port.vid:04X}:{port.pid:04X}"
        print(f"Found device: {port.device} ({vid_pid})")
        if vid_pid in DEVICE_IDS[target]:
            print(f"Found matching device at: {port.device}")
            return port.device

    print(f"Error: No {target} device found")
    return None
