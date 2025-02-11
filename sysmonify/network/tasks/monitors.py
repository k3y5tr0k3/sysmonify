"""monitors.py.

A module for monitoring real-time network stats such as transfer-rates, packet stats
and more.

Classes:
    NetworkMonitor:
        A class for retrieving real-time network statistics.
"""

import datetime

from sysmonify.core.tasks import Monitor
from network.tasks.utils import get_physical_network_interfaces, IP


class NetworkMonitor(Monitor):
    """A class for retrieving real-time network statistic for all network interfaces on the system.

    Methods:
        get_metrics() -> dict:
            Retrieve a dictionary of real-time network statistics for all network
            interfaces. Returns the Mbps values of RX and TX, and the number of packets
            dropped since the previous call.
    """

    def __init__(self):
        """Default initializer."""
        self._previous_network_stats = {}
        self._previous_timestamp = datetime.datetime.now()

    async def get_metrics(self):
        """Retrieve network metrics and return a metrics dictionary.

        Gathers real-time metrics for all physical network interfaces. These metrics
        include:
            - RX mbps
            - TX mbps
            - Dropped packets

        Returns:
            dict:
                {
                    "rx_mbps": 0.123,
                    "tx_mbps": 0.00023,
                    "rx_dropped": 2,
                    "tx_dropped": 0
                }
        """
        metrics = {}
        interfaces = get_physical_network_interfaces()
        current_network_stats = {}
        current_timestamp = datetime.datetime.now()

        for interface in interfaces:
            current_network_stats[interface] = await IP.get_interface_stats(
                interface_name=interface
            )

            if self._previous_network_stats.get(interface, None):
                rx_bytes_delta = (
                    current_network_stats[interface]["rx"]["bytes"]
                    - self._previous_network_stats[interface]["rx"]["bytes"]
                )
                tx_bytes_delta = (
                    current_network_stats[interface]["tx"]["bytes"]
                    - self._previous_network_stats[interface]["tx"]["bytes"]
                )
                rx_dropped_delta = (
                    current_network_stats[interface]["rx"]["dropped"]
                    - self._previous_network_stats[interface]["rx"]["dropped"]
                )
                tx_dropped_delta = (
                    current_network_stats[interface]["tx"]["dropped"]
                    - self._previous_network_stats[interface]["tx"]["dropped"]
                )

                seconds = (current_timestamp - self._previous_timestamp).seconds
                rx_mbps = (
                    rx_bytes_delta / 1024 / 1024 / seconds if rx_bytes_delta > 0 else 0
                )
                tx_mbps = (
                    tx_bytes_delta / 1024 / 1024 / seconds if tx_bytes_delta > 0 else 0
                )

                metrics[interface] = {
                    "rx_mbps": rx_mbps,
                    "tx_mbps": tx_mbps,
                    "rx_dropped": rx_dropped_delta,
                    "tx_dropped": tx_dropped_delta,
                }

        self._previous_timestamp = current_timestamp
        self._previous_network_stats = current_network_stats

        return metrics
