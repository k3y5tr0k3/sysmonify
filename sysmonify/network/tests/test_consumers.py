"""test_consumers.py.

This module contains unit tests for the NetworkConsumer.
"""

from django.test import TestCase
from channels.testing import WebsocketCommunicator

from network.consumers import NetworkConsumer


class TestNetworkConsumer(TestCase):
    """Tests for NetworkConsumer."""

    # TODO: Ensure monitor has default values it can return for GitHub Action Tests to pass
    # async def test_periodic_network_message(self):
    #     """Test that the consumer sends periodic messages containing network metrics.

    #     Assert:
    #         "details" and "stats" and "connections" keys are present in the message.
    #     """
    #     communicator = WebsocketCommunicator(NetworkConsumer.as_asgi(), "ws/network/")
    #     connected, subprotocol = await communicator.connect()
    #     self.assertTrue(connected)

    #     periodic_response = await communicator.receive_json_from()
    #     self.assertIn("details", periodic_response)
    #     self.assertIn("stats", periodic_response)
    #     self.assertIn("connections", periodic_response)

    #     await communicator.disconnect()

    async def test_websocket_disconnect(self):
        """Test that disconnecting from the NetworkConsumer websocket does not raise an exception."""
        communicator = WebsocketCommunicator(NetworkConsumer.as_asgi(), "ws/network/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()
