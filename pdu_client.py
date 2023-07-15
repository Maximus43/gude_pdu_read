"""
This module contains the PduDevice class for communicating with the PDU Gude 8311-1 device.

The PduDevice class has methods for creating a socket connection to the device and searching for devices.
"""

import socket
import struct
import time
from _socket import timeout


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