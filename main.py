"""
A Python script to interact with the PDU Gude 8311-1 device.

It provides options to log and print usage in kilowatts and reset the counter of the device.

Usage:
python main.py interface_name --action action_name --log_file file_path --port port_number
"""

import argparse
import sys

from actions import log_usage_in_kw, print_usage_in_kw, reset_counter
from pdu_client import PduDevice

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