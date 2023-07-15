"""
This module contains the action functions to interact with the PDU Gude 8311-1 device.

Available functions:
- log_usage_in_kw: Logs the power usage in kilowatts from the device to a specified file.
- print_usage_in_kw: Prints the power usage in kilowatts from the device to the stdout.
- reset_counter: Resets the counter of the device.
"""

import telnetlib
from datetime import datetime


def log_usage_in_kw(host, args):
    """
    Log the usage in kilowatts from the device.

    Parameters:
    host (str): The IP address of the host.
    args (Namespace): The command-line arguments.

    Returns:
    None
    """
    value = execute_command(host, args.port, command="linesensor 1 9 value show")
    if not value:
        value = "N/A"
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    output = f"{timestamp} - {value}"
    with open(args.log_file_path, "a") as file:
        file.write(output + "\n")


def print_usage_in_kw(host, args):
    """
    Print usage in kilowatts to stdout.

    Parameters:
    host (str): The IP address of the host.
    args (Namespace): The command-line arguments.

    Returns:
    None
    """
    value = execute_command(host, args.port, command="linesensor 1 9 value show")
    if value is not None:
        print(value)


def reset_counter(host, args):
    """
    Reset the counter of the device.

    Parameters:
    host (str): The IP address of the host.
    args (Namespace): The command-line arguments.

    Returns:
    None
    """
    execute_command(host, args.port, command="linesensor 1 counter reset")


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