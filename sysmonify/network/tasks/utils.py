"""utils.py.

A collection of utility functions and classes for interfacing with command-line
utilities, for network tasks.

Functions:
    get_physical_network_interfaces() -> set:
        Retrieves a set of physical network interface names on the system.

Classes:
    IP:
        A static class for asynchronously interfacing with the linux 'ip' command-line
        utility.

    IW:
        A static class for asynchronously interfacing with the linux 'iw' command-line
        utility.
"""

import os
import re
import logging

from sysmonify.core.utils import run_command_async


logger = logging.getLogger(__name__)


def get_physical_network_interfaces() -> set:
    """Retrieves a set of physical network interface names on the system.

    Gathers a list of interface names based on directories present in `/sys/class/net/`
    and then filters out interfaces where `/sys/class/net/{interface_name}/device` does
    not exist.

    Returns:
        set[str]:
            A set of physical network interface names.
    """
    physical_interfaces = {}

    try:
        interfaces = os.listdir("/sys/class/net/")
        physical_interfaces = {
            interface
            for interface in interfaces
            if os.path.exists(f"/sys/class/net/{interface}/device")
        }

    except Exception as e:
        logger.exception(
            "Error occurred while retrieving a list of physical network interface "
            f"names. {e}"
        )
    return physical_interfaces


class IP:
    """A static class for asynchronously interfacing with the linux 'ip' command-line utility.

    Methods:
        get_ip_addresses(interface_name: str, ip_type: int = 4) -> list:
            Retrieve a list of IP addresses of a given type associated with a given
            network interface.

        get_interface_stats(interface_name: str) -> dict:
            Retrieve statistics for a given network interface.
    """

    @staticmethod
    async def get_ip_addresses(interface_name: str, ip_type: int = 4) -> list:
        """Runs the 'ip' and filters output for a IP addresses of a given type.

        Runs the 'ip' command-line utility for a give ip address type and a given
        network interface returns a list of associated IP addresses.

        Args:
            interface_name (str):
                The name of a network interface.

            ip_type (int):
                IP address type (i.e., 4 = IPv4, 6 = IPv6). Default: 4.

        Returns:
            list[str]:
                A list of IP addresses.
        """
        ip_addresses = []
        command = ["ip", f"-{ip_type}", "addr", "show", f"{interface_name}"]

        try:
            output = await run_command_async(command=command)

            if output["exit_code"] != 0:
                raise Exception(output["stderr"])

            output_lines = output["stdout"].split("\n")
            output_lines = [line.strip("\n") for line in output_lines]

            for line in output_lines:
                if "inet" in line:
                    ip_address = line.strip().split()[1].split("/")[0]
                    ip_addresses.append(ip_address)

        except Exception as e:
            logger.exception(
                f"Error occurred when running the 'ip' command-line utility - {e}"
            )

        return ip_addresses

    async def get_interface_stats(interface_name: str) -> dict:
        """Retrieve details network statistics for a given network interface."""
        stats = {}
        command = ["ip", "-s", "link", "show", f"{interface_name}"]

        try:
            output = await run_command_async(command=command)

            if output["exit_code"] != 0:
                raise Exception(output["stderr"])

            output_lines = output["stdout"].split("\n")
            output_lines = [line.strip("\n") for line in output_lines]

            for i, line in enumerate(output_lines):
                parts = [part.strip() for part in line.split()]

                if not parts:
                    continue

                if parts[1] == f"{interface_name}:":
                    stats["flags"] = parts[2].strip("<>").split(",")
                    stats["rx"] = {}
                    stats["tx"] = {}

                elif parts[0] == "RX:":
                    rx_values = list(map(int, output_lines[i + 1].split()))
                    stats["rx"] = {
                        "bytes": int(rx_values[0]),
                        "packets": int(rx_values[1]),
                        "errors": int(rx_values[2]),
                        "dropped": int(rx_values[3]),
                        "missed": int(rx_values[4]),
                        "multicast": int(rx_values[5]),
                    }

                elif parts[0] == "TX:":
                    tx_values = list(map(int, output_lines[i + 1].split()))
                    stats["tx"] = {
                        "bytes": int(tx_values[0]),
                        "packets": int(tx_values[1]),
                        "errors": int(tx_values[2]),
                        "dropped": int(tx_values[3]),
                        "carrier": int(tx_values[4]),
                        "collisions": int(tx_values[5]),
                    }

        except Exception as e:
            logger.exception(
                f"Error occurred when running the 'ip' command-line utility - {e}"
            )

        return stats


class IW:
    """A static class for asynchronously interfacing with the linux 'iw' command-line utility.

    Methods:
        get_wifi_info(interface_name: str) -> dict:
            Retrieves realtime Wifi information such as SSID, RX, TX and signal
            strength.

    Note:
        The 'iw' command-line utility is the modern replacement for the 'iwconfig'
        command-line utility. It may not be pre-installed on legacy or embedded OSs.
    """

    async def get_wifi_info(interface_name: str) -> dict:
        """Runs 'iw' command for a given network interface and parses the output to a dictionary.

        Retrieves WiFi information for a given network interface such as SSID, RX data,
        TX data, signal strength and more. Parses the data and returns a dictionary. If
        the network interface is not a wireless interface, an empty dictionary is
        returned.

        Args:
            interface_name (str):
                Name of a network interface.

        Returns:
            dict:
                A dictionary with the following keys:
                    - bssid
                    - ssid
                    - frequency
                    - rx_bytes
                    - rx_packets
                    - tx_bytes
                    - tx_packets
                    - signal_dbm
                    - tx_bitrate
        """
        wifi_info = {}
        command = ["iw", "dev", interface_name, "link"]

        try:
            output = await run_command_async(command=command)

            if output["exit_code"] != 0:
                raise Exception(output["stderr"])

            output_lines = output["stdout"].split("\n")
            for line in output_lines:
                line = line.strip()

                if line.startswith("Connected to"):
                    wifi_info["bssid"] = line.split()[2]

                elif line.startswith("SSID:"):
                    wifi_info["ssid"] = line.split(": ", 1)[1]

                elif line.startswith("freq:"):
                    wifi_info["frequency"] = line.split(": ")[1]

                elif line.startswith("RX:"):
                    match = re.search(r"(\d+) bytes \((\d+) packets\)", line)
                    if match:
                        wifi_info["rx_bytes"] = int(match.group(1))
                        wifi_info["rx_packets"] = int(match.group(2))

                elif line.startswith("TX:"):
                    match = re.search(r"(\d+) bytes \((\d+) packets\)", line)
                    if match:
                        wifi_info["tx_bytes"] = int(match.group(1))
                        wifi_info["tx_packets"] = int(match.group(2))

                elif line.startswith("signal:"):
                    wifi_info["signal_dbm"] = int(line.split(": ")[1].split()[0])

                elif line.startswith("tx bitrate:"):
                    wifi_info["tx_bitrate"] = line.split(": ")[1]

        except Exception as e:
            logging.exception(
                "Error occurred while retrieving and parsing wifi info for interface"
                f"`{interface_name}`. {e}"
            )

        return wifi_info
