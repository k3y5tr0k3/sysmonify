"""test_consumers.py.

This module contains unit tests for gpu.consumers
"""

from django.test import TestCase
from channels.testing import WebsocketCommunicator

from gpu.consumers import GPUConsumer


class TestGPUConsumer(TestCase):
    """Tests for GPUConsumer."""

    async def test_websocket_connect_and_receive_initial_details(self):
        """Test that on connection, the consumer sends a message containing GPU details.

        Asserts:
            'details' key is present in initial message sent.
        """
        communicator = WebsocketCommunicator(GPUConsumer.as_asgi(), "ws/gpu/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        self.assertIn("details", response)

        await communicator.disconnect()

    async def test_periodic_cpu_metrics_message(self):
        """Test that the consumer sends periodic messages containing GPU metrics.

        Assets:
            Key in the periodic message is "metrics".
        """
        communicator = WebsocketCommunicator(GPUConsumer.as_asgi(), "ws/gpu/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        initial_response = await communicator.receive_json_from()
        self.assertIn("details", initial_response)

        periodic_response = await communicator.receive_json_from()
        self.assertIn("metrics", periodic_response)

        await communicator.disconnect()

    async def test_websocket_disconnect(self):
        """Test that disconnecting from the GPUConsumer websocket does not raise an exception."""
        communicator = WebsocketCommunicator(GPUConsumer.as_asgi(), "ws/gpu/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()
