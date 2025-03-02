"""consumers.py.

A module containing WebSocket Consumers for the network app.

Classes:
    NetworkConsumer:
        WebSocket consumer for handling real-time system network statistic and
        connections updates to the client.
"""

from sysmonify.core.consumers import Consumer

from network.tasks.details import NetworkDetails
from network.tasks.monitors import NetworkStatsMonitor, NetworkConnectionsMonitor


class NetworkConsumer(Consumer):
    """WebSocket consumer for handling real-time system network metrics updates to the client.

    Methods:
        get_message_data() -> dict:
            Retrieves network details, and real-time metrics and returns the data in a
            dictionary.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Default initializer."""
        super().__init__(*args, **kwargs)

        self.net_stat_monitor = NetworkStatsMonitor()
        self.net_con_monitor = NetworkConnectionsMonitor()
        self.net_details = NetworkDetails()

    async def get_message_data(self) -> dict:
        """Retrieve network metrics and return the data as a dictionary.

        Returns:
            dict:
                A dictionary containing upto date network metrics such as temperature
                and utilization.
        """
        net_metrics = {
            "details": await self.net_details.get_details(),
            "stats": await self.net_stat_monitor.get_metrics(),
            "connections": self.net_con_monitor.get_metrics(),
        }

        return net_metrics
