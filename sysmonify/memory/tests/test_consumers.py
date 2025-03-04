"""test_consumers.py.

This module contains unit tests for memory.consumers
"""

from django.test import TestCase
from channels.testing import WebsocketCommunicator

from memory.consumers import MemoryConsumer


class TestMemoryConsumer(TestCase):
    """Tests for MemoryConsumer."""

    async def test_periodic_memory_metrics_message(self):
        """Test that the consumer sends periodic messages containing memory metrics.

        Assets:
            Keys in the periodic message are "memory" and "swap".
        """
        communicator = WebsocketCommunicator(MemoryConsumer.as_asgi(), "ws/memory/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        periodic_response = await communicator.receive_json_from()
        self.assertIn("metrics", periodic_response)
        self.assertIn("memory", periodic_response["metrics"])
        self.assertIn("swap", periodic_response["metrics"])

        await communicator.disconnect()

    async def test_websocket_disconnect(self):
        """Test that disconnecting from the MemoryConsumer websocket does not raise an exception."""
        communicator = WebsocketCommunicator(MemoryConsumer.as_asgi(), "ws/memory/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()
