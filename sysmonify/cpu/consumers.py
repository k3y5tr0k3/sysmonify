"""consumers.py.

A module containing WebSocket Consumers for the dashboard app.

Classes:
    `CPUConsumer`:
        WebSocket consumer for handling real-time system CPU metrics updates to the
        client.
"""

import json

from sysmonify.core.consumers import Consumer

from cpu.tasks.details import CPUDetails
from cpu.tasks.monitors import CPUFreqMonitor, CPUThermalMonitor


class CPUConsumer(Consumer):
    """WebSocket consumer for handling real-time system CPU metrics updates to the client.

    Methods:
        `get_message_data()`:
            Retrieves CPU details, and real-time metrics and returns the data in a
            dictionary.
    """

    def __init__(self, *args, **kwargs):
        """Default initializer."""
        super().__init__(*args, **kwargs)

        self.freq_monitor = CPUFreqMonitor()
        self.temp_monitor = CPUThermalMonitor()

    async def connect(self) -> None:
        """Handles a new WebSocket connection.

        Accepts a websocket connection from the client, send initial message containing
        static CPU details, and calls the `send_message_periodically()` method.
        """
        await self.accept()

        cpu_details = {"details": await CPUDetails().get_details()}
        await self.send(text_data=json.dumps(cpu_details))
        await self.send_message_periodically()

    async def get_message_data(self) -> dict:
        """Retrieve CPU metrics from various CPU monitors and return the data as a dictionary."""
        cpu_metrics = {
            "freq": await self.freq_monitor.get_metrics(),
            "temp": await self.temp_monitor.get_metrics(),
        }

        return cpu_metrics
