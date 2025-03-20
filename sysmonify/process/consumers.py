"""consumers.py.

A module containing WebSocket Consumers for the process app.

Classes:
    ProcessConsumer:
        WebSocket consumer for handling real-time system process metrics updates to the
        client.
"""

from sysmonify.core.consumers import Consumer
from process.tasks.monitors import ProcessMonitor


class ProcessConsumer(Consumer):
    """WebSocket consumer for handling real-time system GPU metrics updates to the client.

    Methods:
        get_message_data() -> dict:
            Retrieves real-time process metrics and returns the data in a dictionary.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Default initializer."""
        super().__init__(*args, **kwargs)

        self.process_monitor = ProcessMonitor()

    async def get_message_data(self) -> dict:
        """Retrieve process metrics and return the data as a dictionary.

        Returns:
            dict:
                A dictionary containing upto date process metrics.
        """
        gpu_metrics = {
            "metrics": await self.process_monitor.get_metrics(),
        }

        return gpu_metrics
