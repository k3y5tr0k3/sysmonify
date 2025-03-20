"""test_consumers.py.

This module contains unit tests for the ProcessConsumer.
"""

from django.test import TestCase
from channels.testing import WebsocketCommunicator

from process.consumers import ProcessConsumer


class TestProcessConsumer(TestCase):
    """Tests for ProcessConsumer."""

    async def test_periodic_process_message(self):
        """Test that the consumer sends periodic messages containing process metrics.

        Assert:
            "metrics" keys is present in the message.
        """
        communicator = WebsocketCommunicator(ProcessConsumer.as_asgi(), "ws/processes/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        periodic_response = await communicator.receive_json_from()
        self.assertIn("metrics", periodic_response)

        await communicator.disconnect()

    async def test_websocket_disconnect(self):
        """Test that disconnecting from the NetworkConsumer websocket does not raise an exception."""
        communicator = WebsocketCommunicator(ProcessConsumer.as_asgi(), "ws/processes/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()
