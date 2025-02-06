"""consumers.py.

A module containing WebSocket Consumers for the disk app.

Classes:
    `DiskConsumer`:
        WebSocket consumer for handling real-time system disk details/metrics updates to the
        client.
"""

import logging

from disk.tasks.details import DiskDetails
from disk.tasks.monitors import DiskIOMonitor
from sysmonify.core.consumers import Consumer


logger = logging.getLogger(__name__)


class DiskConsumer(Consumer):
    """WebSocket consumer for handling real-time system disk details/metrics updates to the client.

    Methods:
        `get_message_data()`:
            Retrieves disk details, and real-time metrics and returns the data in a
            dictionary.
    """

    def __init__(self, *args, **kwargs):
        """Default initializer."""
        super().__init__(*args, **kwargs)

        self.disk_details = DiskDetails()
        self.io_monitor = DiskIOMonitor(disks=[])

    async def get_message_data(self) -> dict:
        """Retrieve CPU metrics from various CPU monitors and return the data as a dictionary."""
        disks = await self.disk_details.get_details()
        disk_names = [disk["name"] for disk in disks]
        self.io_monitor.disks = disk_names
        disks_speeds = self.io_monitor.get_metrics()

        disks = {"disks": disks, "disks_speeds": disks_speeds}

        return disks
