"""test_consumers.py.

This module contains unit tests for cpu.consumers
"""

from django.test import TestCase
from channels.testing import WebsocketCommunicator

from cpu.consumers import CPUConsumer


class TestCPUConsumer(TestCase):
    """Tests for CPUConsumer."""

    async def test_websocket_connect_and_receive_initial_details(self):
        """Test that on connection, the consumer sends a message containing CPU details.

        Asserts:
            'details' key is present in initial message sent.
        """
        communicator = WebsocketCommunicator(CPUConsumer.as_asgi(), "ws/cpu/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        self.assertIn("details", response)

        await communicator.disconnect()

    async def test_periodic_cpu_metrics_message(self):
        """Test that the consumer sends periodic messages containing CPU metrics.

        Assets:
            Keys in the periodic message are "freq" and "temp".
        """
        communicator = WebsocketCommunicator(CPUConsumer.as_asgi(), "ws/cpu/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        initial_response = await communicator.receive_json_from()
        self.assertIn("details", initial_response)

        periodic_response = await communicator.receive_json_from()
        self.assertIn("freq", periodic_response)
        self.assertIn("temp", periodic_response)

        await communicator.disconnect()

    async def test_websocket_disconnect(self):
        """Test that disconnecting from the CPUConsumer websocket does not raise an exception."""
        communicator = WebsocketCommunicator(CPUConsumer.as_asgi(), "ws/cpu/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()
