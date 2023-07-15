# PDU Gude 8311-1 Device Interaction Tool
This tool provides a simple command-line interface to interact with PDU Gude 8311-1 devices. It allows you to log and print usage in kilowatts and reset the counter of the device.
## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

## Prerequisites
This tool requires Python 3.7 or newer.

## Installation
Clone the repository to your local machine:

```git clone https://github.com/Maximus43/gude_pdu_read.git```

## Usage

To use this tool, you'll need to run the main.py script with the appropriate arguments.

Here is the general usage:

```python main.py interface_name --action action_name --log_file file_path --port port_number```

- *interface_name* is the network interface to bind to.
- *--action* is the action to perform. It can be one of the following: "log_usage_in_kw", "reset_counter", or "print_usage_in_kw". The default action is "print_usage_in_kw".
- *--log_file* is the file path for logging usage data. The default file path is "./stat.txt".
- *--port* is the port number to use for the connection. The default port number is 23

For example, to log the usage in kilowatts from the device, use the following command:

```python main.py eth0 --action log_usage_in_kw --log_file ./usage_log.txt --port 23```

# Using with cron for Scheduled Tasks

If you need to perform actions such as logging usage or resetting the counter at specific times, you can use cron to schedule these tasks.

For example, you can add the following lines to your crontab to log usage at 11:59 PM every day and reset the counter at midnight on the first day of each month:

```
59 23 * * * python /usr/share/app/pdu/main.py eth0 --action=log_usage_in_kw --log_file ./usage_log.txt
0 0 1 * * python /usr/share/app/pdu/main.py eth0 --action=reset_counter
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
