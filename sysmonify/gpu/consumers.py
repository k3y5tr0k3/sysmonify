"""consumers.py.

A module containing WebSocket Consumers for the GPU app.

Classes:
    GPUConsumer:
        WebSocket consumer for handling real-time system GPU metrics updates to the
        client.
"""

import json

from sysmonify.core.consumers import Consumer

from gpu.tasks.details import GPUDetails
from gpu.tasks.monitors import GPUMonitor


class GPUConsumer(Consumer):
    """WebSocket consumer for handling real-time system GPU metrics updates to the client.

    Methods:
        get_message_data() -> dict:
            Retrieves GPU details, and real-time metrics and returns the data in a
            dictionary.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Default initializer."""
        super().__init__(*args, **kwargs)

        self.gpu_monitor = GPUMonitor()

    async def connect(self):
        """Handles a new WebSocket connection.

        Accepts a websocket connection from the client, send initial message containing
        static GPU details, and calls the `send_message_periodically()` method.
        """
        await self.accept()

        gpu_details = {"details": await GPUDetails().get_details()}
        await self.send(text_data=json.dumps(gpu_details))
        await self.send_message_periodically()

    async def get_message_data(self) -> dict:
        """Retrieve GPU metrics and return the data as a dictionary.

        Returns:
            dict:
                A dictionary containing upto date GPU metrics such as temperature and
                utilization.
        """
        gpu_metrics = {
            "metrics": await self.gpu_monitor.get_metrics(),
        }

        return gpu_metrics
