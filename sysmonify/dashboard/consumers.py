"""consumers.py.

A module containing WebSocket Consumers for the dashboard app.
"""

import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer


logger = logging.getLogger(__name__)


class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for handling real-time dashboard updates.

    This consumer allows clients to connect to a WebSocket endpoint
    and receive live system metrics, such as CPU usage, memory usage.

    Methods:
        connect: Handles a new WebSocket connection.
        disconnect: Handles WebSocket disconnections.
        receive: Handles incoming messages from the WebSocket client.
    """

    async def connect(self) -> None:
        """Handles a new WebSocket connection.

        The method accepts the WebSocket connection, adds the client
        to a group for broadcasting metrics, and sends an initial
        success message.
        """
        await self.accept()

        # Example of sending initial metrics data (you would replace this with actual data)
        metrics_data = {"cpu_usage": 50, "memory_usage": 65, "disk_usage": 40}
        await self.send(text_data=json.dumps(metrics_data))

    async def disconnect(self, close_code: int) -> None:
        """Handles WebSocket disconnections.

        Removes the client from the metrics group when the connection is closed.

        Args:
            close_code (int): The WebSocket close code.
        """
        pass

    async def receive(self, json: str) -> None:
        """Handles incoming messages from the WebSocket client.

        This method processes messages sent by the client. If necessary,
        it can be extended to handle commands or actions requested by
        the client.

        Args:
            json (str): The raw JSON message received from the client.

        Raises:
            ValueError: If the `text_data` is not valid JSON.
        """
        pass


class ProcessesConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for handling real-time system process updates.

    This consumer allows clients to connect to a WebSocket endpoint
    and receive live system metrics, such as the total number of processes, their
    individual cpu and memory usage.

    Methods:
        connect: Handles a new WebSocket connection.
        disconnect: Handles WebSocket disconnections.
        receive: Handles incoming messages from the WebSocket client.
    """

    async def connect(self) -> None:
        """Handles a new WebSocket connection.

        The method accepts the WebSocket connection, adds the client
        to a group for broadcasting metrics, and sends an initial
        success message.
        """
        await self.accept()

        system_processes = {"pid": 50, "user": "system-user", "name": 40}
        await self.send(text_data=json.dumps(system_processes))

    async def disconnect(self, close_code: int) -> None:
        """Handles WebSocket disconnections.

        Removes the client from the metrics group when the connection is closed.

        Args:
            close_code (int): The WebSocket close code.
        """
        pass

    async def receive(self, json: str) -> None:
        """Handles incoming messages from the WebSocket client.

        This method processes messages sent by the client. If necessary,
        it can be extended to handle commands or actions requested by
        the client.

        Args:
            json (str): The raw JSON message received from the client.

        Raises:
            ValueError: If the `text_data` is not valid JSON.
        """
        pass


class MemoryConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for handling real-time system memory updates.

    This consumer allows clients to connect to a WebSocket endpoint
    and receive live system metrics, such as the memory usage.

    Methods:
        connect: Handles a new WebSocket connection.
        disconnect: Handles WebSocket disconnections.
        receive: Handles incoming messages from the WebSocket client.
    """

    async def connect(self) -> None:
        """Handles a new WebSocket connection.

        The method accepts the WebSocket connection, adds the client
        to a group for broadcasting metrics, and sends an initial
        success message.
        """
        await self.accept()

        system_processes = {"core_id": 5, "freq": 1400, "temp": 40}
        await self.send(text_data=json.dumps(system_processes))

    async def disconnect(self, close_code: int) -> None:
        """Handles WebSocket disconnections.

        Removes the client from the metrics group when the connection is closed.

        Args:
            close_code (int): The WebSocket close code.
        """
        pass

    async def receive(self, json: str) -> None:
        """Handles incoming messages from the WebSocket client.

        This method processes messages sent by the client. If necessary,
        it can be extended to handle commands or actions requested by
        the client.

        Args:
            json (str): The raw JSON message received from the client.

        Raises:
            ValueError: If the `text_data` is not valid JSON.
        """
        pass


class GPUConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for handling real-time system GPU updates.

    This consumer allows clients to connect to a WebSocket endpoint
    and receive live system metrics, such as the gpu utilization and vram usage.

    Methods:
        connect: Handles a new WebSocket connection.
        disconnect: Handles WebSocket disconnections.
        receive: Handles incoming messages from the WebSocket client.
    """

    async def connect(self) -> None:
        """Handles a new WebSocket connection.

        The method accepts the WebSocket connection, adds the client
        to a group for broadcasting metrics, and sends an initial
        success message.
        """
        await self.accept()

        system_processes = {"core_id": 5, "freq": 1400, "temp": 40}
        await self.send(text_data=json.dumps(system_processes))

    async def disconnect(self, close_code: int) -> None:
        """Handles WebSocket disconnections.

        Removes the client from the metrics group when the connection is closed.

        Args:
            close_code (int): The WebSocket close code.
        """
        pass

    async def receive(self, json: str) -> None:
        """Handles incoming messages from the WebSocket client.

        This method processes messages sent by the client. If necessary,
        it can be extended to handle commands or actions requested by
        the client.

        Args:
            json (str): The raw JSON message received from the client.

        Raises:
            ValueError: If the `text_data` is not valid JSON.
        """
        pass


class NetworkConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for handling real-time system network updates.

    This consumer allows clients to connect to a WebSocket endpoint
    and receive live system metrics, such as the network usage and connections.

    Methods:
        connect: Handles a new WebSocket connection.
        disconnect: Handles WebSocket disconnections.
        receive: Handles incoming messages from the WebSocket client.
    """

    async def connect(self) -> None:
        """Handles a new WebSocket connection.

        The method accepts the WebSocket connection, adds the client
        to a group for broadcasting metrics, and sends an initial
        success message.
        """
        await self.accept()

        system_processes = {"core_id": 5, "freq": 1400, "temp": 40}
        await self.send(text_data=json.dumps(system_processes))

    async def disconnect(self, close_code: int) -> None:
        """Handles WebSocket disconnections.

        Removes the client from the metrics group when the connection is closed.

        Args:
            close_code (int): The WebSocket close code.
        """
        pass

    async def receive(self, json: str) -> None:
        """Handles incoming messages from the WebSocket client.

        This method processes messages sent by the client. If necessary,
        it can be extended to handle commands or actions requested by
        the client.

        Args:
            json (str): The raw JSON message received from the client.

        Raises:
            ValueError: If the `text_data` is not valid JSON.
        """
        pass


class IOConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for handling real-time system IO updates.

    This consumer allows clients to connect to a WebSocket endpoint
    and receive live system metrics, such as the throughput and disk health.

    Methods:
        connect: Handles a new WebSocket connection.
        disconnect: Handles WebSocket disconnections.
        receive: Handles incoming messages from the WebSocket client.
    """

    async def connect(self) -> None:
        """Handles a new WebSocket connection.

        The method accepts the WebSocket connection, adds the client
        to a group for broadcasting metrics, and sends an initial
        success message.
        """
        await self.accept()

        system_processes = {"core_id": 5, "freq": 1400, "temp": 40}
        await self.send(text_data=json.dumps(system_processes))

    async def disconnect(self, close_code: int) -> None:
        """Handles WebSocket disconnections.

        Removes the client from the metrics group when the connection is closed.

        Args:
            close_code (int): The WebSocket close code.
        """
        pass

    async def receive(self, json: str) -> None:
        """Handles incoming messages from the WebSocket client.

        This method processes messages sent by the client. If necessary,
        it can be extended to handle commands or actions requested by
        the client.

        Args:
            json (str): The raw JSON message received from the client.

        Raises:
            ValueError: If the `text_data` is not valid JSON.
        """
        pass
