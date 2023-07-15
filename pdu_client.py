"""
A Python script to interact with the PDU Gude 8311-1 device.

It provides options to log and print usage in kilowatts and reset the counter of the device.

Usage:
python pdu_client.py interface_name --action action_name --log_file file_path --port port_number
"""

import argparse
import socket
import struct
import sys
import telnetlib
import time
from _socket import timeout
from datetime import datetime


class PduDevice(object):
    """
    A class to represent a PDU device.

    ...

    Attributes:
    sock : socket
        a socket for communicating with the PDU device

    Methods:
    search(max_wait=3.0, expected_devs=None):
        Search for devices and return a list of found devices.
    """

    sock: socket

    def __init__(self, interface):
        """
        Constructs all the necessary attributes for the PduDevice object.

        Parameters:
        interface (str): the network interface to bind to
        """

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Bind the socket to a specific interface
        try:
            self.sock.setsockopt(
                socket.SOL_SOCKET, 25, struct.pack("256s", bytes(interface, "utf-8"))
            )
        except OSError:
            print("Unable to bind to interface {}".format(interface))
        except Exception as e:
            print(e)
            raise e

    def search(self, max_wait=3.0, expected_devs=None):
        """
        Search for devices and return a list of found devices.

        Parameters:
        max_wait (float): the maximum time to wait for a response from a device
        expected_devs (int): the expected number of devices

        Returns:
        list: a list of found devices
        """

        # 'GBL' '4' '1' 0x4c
        self.sock.sendto(b"\x47\x42\x4c\x04\x01\x4c", ("255.255.255.255", 50123))

        self.sock.settimeout(1)
        started_time = time.time()
        num_devices = 0
        _device_list = []

        while True:
            try:
                data, _ = self.sock.recvfrom(1024)
                gbl_reply = {
                    "version": int(data[3]),
                    "command": int(data[4]),
                    "mac": ":".join(f"{c:02x}" for c in data[5:11]),
                }
                if (gbl_reply["version"] == 4) and (gbl_reply["command"] == 1):
                    num_devices += 1
                    gbl_reply["bootloader"] = int(data[17:18][0])
                    gbl_reply["ip"] = ".".join(f"{c}" for c in data[18:22])
                    _device_list.append(gbl_reply)

                if expected_devs is not None and expected_devs == num_devices:
                    return _device_list

            except timeout:
                pass

            this_time = time.time()
            if this_time - started_time >= max_wait:
                break

        return num_devices

    def __del__(self):
        """
        Destroys the PduDevice object and closes the socket connection.
        """

        self.sock.close()


def log_usage_in_kw(host, _args):
    """
    Log the usage in kilowatts from the device.

    Parameters:
    host (str): The IP address of the host.
    args (Namespace): The command-line arguments.

    Returns:
    None
    """
    value = execute_command(host, _args.port, command="linesensor 1 9 value show")
    if not value:
        value = "N/A"
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    output = f"{timestamp} - {value}"
    with open(_args.log_file_path, "a") as file:
        file.write(output + "\n")


def print_usage_in_kw(host, _args):
    """
    Print usage in kilowatts to stdout.

    Parameters:
    host (str): The IP address of the host.
    args (Namespace): The command-line arguments.

    Returns:
    None
    """
    value = execute_command(host, _args.port, command="linesensor 1 9 value show")
    if value is not None:
        print(value)


def reset_counter(host, _args):
    """
    Reset the counter of the device.

    Parameters:
    host (str): The IP address of the host.
    args (Namespace): The command-line arguments.

    Returns:
    None
    """
    execute_command(host, _args.port, command="linesensor 1 counter reset")


def execute_command(host, port, command):
    """
    Executes a command on the device.

    Parameters:
    host (str): The IP address of the host.
    port (int): The port number for the connection.
    command (str): The command to execute.

    Returns:
    str: The output from the command execution.
    """
    try:
        tn = telnetlib.Telnet(host, port)
        tn.timeout = 1
        tn.write(command.encode("ascii") + b"\n")
        output = tn.read_until(b"\n").decode("ascii").replace(">", "").strip()
        return output
    except Exception as e:
        print(f"Failed to execute command {command} on host {host}:{port}. Error: {str(e)}")
        return None


# Mapping actions to their respective function calls
ACTION_FUNCTION_MAP = {
    "log_usage_in_kw": log_usage_in_kw,
    "print_usage_in_kw": print_usage_in_kw,
    "reset_counter": reset_counter,
}

if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Run GblClient on specific interface.")
    parser.add_argument("interface", type=str, help="The network interface to bind to.")
    parser.add_argument(
        "--action",
        type=str,
        choices=["log_usage_in_kw", "reset_counter", "print_usage_in_kw"],
        help="The action to perform.",
        default="print_usage_in_kw",
    )
    parser.add_argument(
        "--log_file",
        type=str,
        default="./stat.txt",
        help="The file path for logging usage data.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=23,
        help="The port number to use for the connection.",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Instantiate the PduDevice object and search for the device
    pdu = PduDevice(args.interface)
    device_list = pdu.search(max_wait=1.0, expected_devs=1)
    if not device_list:
        print("No devices found.")
        sys.exit(1)

    pdu_device = device_list[0]

    # Perform the specified action
    action_function = ACTION_FUNCTION_MAP.get(args.action)
    if action_function is not None:
        action_function(pdu_device.get("ip"), args)
    else:
        print(f"Invalid action: {args.action}")
        sys.exit(1)