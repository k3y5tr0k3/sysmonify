"""details.py.

Module for gathering static (or semi-static) details on physical network interfaces on
the system.

Classes:
    NetworkDetails:
        A class for retrieving static (or semi-static) details about all physical
        network interfaces on a system.

Example:
    net_details = NetworkDetails()
    details = net_details.get_details()
    print(details.get("ipv4"))
"""

import os
import logging

from sysmonify.core.tasks import Details
from network.tasks.utils import IP, IW, get_physical_network_interfaces


logger = logging.getLogger(__name__)


class NetworkDetails(Details):
    """A class for retrieving static (or semi-static) details about all physical network interfaces on a system.

    Methods:
        _get_interface_mac(interface_name: str) -> str:
            Retrieve the MAC address associated with a given network interface.

        get_details() -> dict:
            Retrieve details about all physical network interfaces on the system and
            return the data in a dictionary.
    """

    def _get_interface_mac(self, interface_name: str) -> str:
        """Retrieve the MAC address associated with a given network interface.

        Retrieves the MAC address for a given network interface name from
        `/sys/class/net/{interface_name}/address`. If or some reason the address cannot
        be retrieved 'Unknown' is returned.

        Args:
            interface_name (str):
                The name of the network interface.

        Returns:
            str:
                The MAC address of the given network interface, or 'Unknown' if it
                cannot be retrieved.

        Raises:
            - FileNotFoundError:
                If the address file does not exist for the given network interface.

            - Exception:
                For all other exceptions raised during retrieval of MAC address.
        """
        mac = "Unknown"
        interface_mac_path = f"/sys/class/net/{interface_name}/address"

        try:
            if os.path.exists(interface_mac_path):
                with open(interface_mac_path, "r") as f:
                    mac = f.read().strip()

        except FileNotFoundError:
            logger.exception(
                "Error occurred while retrieving MAC address for interface "
                f"`{interface_name}` from file `{interface_mac_path}`."
            )

        except Exception as e:
            logging.exception(
                f"An unexpected error occurred while retrieving MAC address for "
                f"interface `{interface_name}` from file `{interface_mac_path}`. {e}"
            )

        return mac

    def _get_interface_mtu(self, interface_name: str) -> str:
        """Retrieves the MTU (Maximum Transmission Unit) for a given interface.

        Retrieves the MTU from `/sys/class/net/{interface_name}/mtu`.

        Args:
            interface_name (str):
                The name of the network interface.

        Returns:
            str:
                The MTU in bytes. Or 'Unknown' if unavailable.

        Raises:
            FileNotFoundError:
                When the mtu file does not exist.

            Exception:
                For a other exceptions.
        """
        mtu = "Unknown"
        interface_mtu_path = f"/sys/class/net/{interface_name}/mtu"

        try:
            if os.path.exists(interface_mtu_path):
                with open(interface_mtu_path, "r") as f:
                    mtu = f.read().strip()

        except FileNotFoundError:
            logger.exception(
                "Error occurred while retrieving MTU for interface "
                f"`{interface_name}` from file `{interface_mtu_path}`."
            )

        except Exception as e:
            logging.exception(
                f"An unexpected error occurred while retrieving MTU for "
                f"interface `{interface_name}` from file `{interface_mtu_path}`. {e}"
            )

        return mtu

    def _get_interface_max_speed(self, interface_name: str) -> str:
        """Retrieve the max link speed for a given interface.

        Retrieves the maximum link speed for a given interface from
        `/sys/class/net/{interface_name}/speed`.

        Args:
            interface_name (str):
                The name of the network interface.

        Returns:
            str:
                Max link speed in megabytes per second. Or 'Unknown' if unavailable.

        Raises:
            FileNotFoundError:
                When speed file does not exist.

            Exception:
                All other exceptions.
        """
        speed = "Unknown"
        interface_speed_path = f"/sys/class/net/{interface_name}/speed"

        try:
            if os.path.exists(interface_speed_path):
                with open(interface_speed_path, "r") as f:
                    speed = f.read().strip()

        except FileNotFoundError:
            logger.exception(
                "Error occurred while retrieving max link speed for interface "
                f"`{interface_name}` from file `{interface_speed_path}`."
            )

        except Exception as e:
            logging.exception(
                f"An unexpected error occurred while retrieving max link speed for "
                f"interface `{interface_name}` from file `{interface_speed_path}`. {e}"
            )

        return speed

    def _get_interface_type(self, interface_name: str) -> str:
        """Retrieve the interface type for a given interface.

        Retrieves the interface type for a given interface name by looking in
        `/sys/class/net/{interface_name}/uevent` file. If "DEVTYPE=wlan" exists in the
        file the interface type is 'WiFi', else we assume the interface type is
        'Ethernet'.

        Args:
            interface_name (str):
                The name of the network interface.

        Returns:
            The interface type.

        Raises:
            FileNotFoundError:
                If uevent file does not exist.

            Exception:
                All other exceptions.
        """
        interface_type = "Ethernet"
        interface_type_path = f"/sys/class/net/{interface_name}/uevent"

        try:
            if os.path.exists(interface_type_path):
                with open(interface_type_path, "r") as f:
                    for line in f:
                        if line.startswith("DEVTYPE=wlan"):
                            interface_type = "WiFi"

        except FileNotFoundError:
            logging.exception(
                "Error occurred while retrieving interface type for interface "
                f"`{interface_name}` from file `{interface_type_path}`."
            )

        except Exception as e:
            logging.exception(
                f"An unexpected error occurred while retrieving interface type for "
                f"interface `{interface_name}` from file `{interface_type_path}`. {e}"
            )

        return interface_type

    async def get_details(self) -> dict:
        """Retrieve details about all physical network interfaces on the system and return the data in a dictionary.

        Gathers network interface details for all physical network interfaces on the
        system, and parses the details in a dictionary.

        Details gathered:
            - Network Interface Name (e.g., 'eth0')
            - MAC Address (e.g., 'A3:CD:0D:00:10:F0')
            - Interface Type (e.g., 'Ethernet' or 'WiFi')
            - IPv4 Address (e.g., '192.176.0.13')
            - IPv6 Address (e.g., '2001:db8:3333:4444:5555:6666:7777:8888')
            - Max Link Speed (e.g., '800 Mbps')
            - Maximum Transmission Unit (e.g., '1500 Bytes')

        Returns:
            dict[dict]:
                {
                    "eth0": {
                        "mac": "A3:CD:0D:00:10:F0",
                        "type": "Ethernet",
                        "ipv4": [
                            "192.176.0.13"
                        ],
                        "ipv6": [
                            "2001:db8:3333:4444:5555:6666:7777:8888"
                        ],
                        "speed": "800 Mbps",
                        "mtu": "1500 Bytes",
                        "additional": {},
                    },
                    ...
                }
        """
        details = {}
        interfaces = get_physical_network_interfaces()

        for interface in interfaces:
            additional_info = {}
            interface_type = self._get_interface_type(interface_name=interface)
            if interface_type == "WiFi":
                additional_info = await IW.get_wifi_info(interface_name=interface)
            details[interface] = {
                "mac": self._get_interface_mac(interface_name=interface),
                "type": interface_type,
                "ipv4": await IP.get_ip_addresses(interface_name=interface),
                "ipv6": await IP.get_ip_addresses(interface_name=interface, ip_type=6),
                "speed": self._get_interface_max_speed(interface_name=interface),
                "mtu": self._get_interface_mtu(interface_name=interface),
                "additional": additional_info,
            }

        return details
