"""consumers.py.

A module with a abstract base `Consumer` that all other consumers inherit from.

Classes:
    `Consumer`:
        An abstract base consumer that all other consumers inherit from.
"""

import abc
import json
import asyncio
import logging

from channels.generic.websocket import AsyncWebsocketConsumer


logger = logging.getLogger(__name__)


class Consumer(AsyncWebsocketConsumer, abc.ABC):
    """Abstract base WebSocket consumer for handling real-time communications with the client.

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
        await self.send_message_periodically()

    async def disconnect(self, close_code: int) -> None:
        """Handles WebSocket disconnections.

        Removes the client from the metrics group when the connection is closed.

        Args:
            close_code (int):
                The WebSocket close code.
        """
        pass

    async def send_message_periodically(self, interval_seconds: float = 1.0) -> None:
        """This function sends messages to the client every `interval_seconds` seconds.

        Args:
            interval_seconds (float):
                The interval time in seconds for the websocket to send messages to the
                client. Default is `1.0` seconds.

        Raises:
            asyncio.CancelledError:
                If the asyncio task is cancelled.
            Exception:
                If an unexpected error occurs during the retrieval of data or sending of
                message.
        """
        try:
            while True:
                message = await self.get_message_data()
                await self.send(text_data=json.dumps(message))
                await asyncio.sleep(interval_seconds)

        except asyncio.exceptions.CancelledError:
            ...

        except Exception as e:
            logger.exception(f"Unexpected error in sending periodic messages: {str(e)}")

        finally:
            try:
                await self.close()

            except Exception as close_error:
                logger.exception(f"Error closing WebSocket: {str(close_error)}")

    @abc.abstractmethod
    async def get_message_data(self) -> dict:
        """Retrieves message data to be sent to the client."""
        ...

    async def receive(self, json: str) -> None:
        """Handles incoming messages from the WebSocket client.

        This method processes messages sent by the client. If necessary,
        it can be extended to handle commands or actions requested by
        the client.

        Args:
            json (str):
                The raw JSON message received from the client.

        Raises:
            ValueError:
                If `json` is not valid JSON.
        """
        pass


class TestConsumer(Consumer):
    """A test subclass of the Consumer class to implement the abstract method."""

    async def get_message_data(self) -> dict:
        """Return a sample message for testing purposes."""
        return {"message": "test message"}
