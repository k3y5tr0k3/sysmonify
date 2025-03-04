"""consumers.py.

A module containing WebSocket Consumers for the memory app.

Classes:
    `MemoryConsumer`:
        WebSocket consumer for handling real-time system memory metrics updates to the
        client.
"""

from sysmonify.core.consumers import Consumer

from memory.tasks.monitors import MemoryMonitor


class MemoryConsumer(Consumer):
    """WebSocket consumer for handling real-time system memory metrics updates to the client.

    Methods:
        `get_message_data()`:
            Retrieves memory real-time metrics and returns the data in a
            dictionary.
    """

    def __init__(self, *args, **kwargs):
        """Default initializer."""
        super().__init__(*args, **kwargs)

        self.mem_monitor = MemoryMonitor()

    async def get_message_data(self) -> dict:
        """Retrieve memory metrics from various memory monitors and return the data as a dictionary."""
        mem_metrics = {
            "metrics": self.mem_monitor.get_metrics(),
        }

        return mem_metrics
