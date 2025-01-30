"""test_consumers.py.

This module contains unit tests for `sysmonify.core.TestConsumer`
"""

from django.test import TestCase
from channels.testing import WebsocketCommunicator

from sysmonify.core import consumers


class TestConsumer(TestCase):
    """Test the base abstract consumer class."""

    async def test_websocket_connect_and_receive_message(self):
        """Test that messages can be received from the client."""
        communicator = WebsocketCommunicator(
            consumers.TestConsumer.as_asgi(), "ws/test/"
        )
        connected, subprotocol = await communicator.connect()

        assert connected

        response = await communicator.receive_json_from()
        assert response == {"message": "test message"}

        await communicator.disconnect()

    async def test_periodic_message_sending(self):
        """Test that messages can be sent to the client periodically."""
        communicator = WebsocketCommunicator(
            consumers.TestConsumer.as_asgi(), "ws/metrics/"
        )
        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        response = await communicator.receive_json_from()

        self.assertEqual(response, {"message": "test message"})

        await communicator.disconnect()

    async def test_websocket_disconnect(self):
        """Test that disconnecting from a websocket does not raise an exception."""
        communicator = WebsocketCommunicator(
            consumers.TestConsumer.as_asgi(), "ws/metrics/"
        )
        connected, subprotocol = await communicator.connect()

        assert connected

        await communicator.disconnect()
