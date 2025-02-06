"""test_disk_consumers.py.

This module contains unit tests for the DiskConsumer.
"""

import asyncio
from django.test import TestCase
from channels.testing import WebsocketCommunicator

from disk.consumers import DiskConsumer


class TestDiskConsumer(TestCase):
    """Tests for DiskConsumer."""

    async def test_websocket_connect_and_receive_initial_disk_details(self):
        """Test that on connection, the consumer sends a message containing disk details.

        Asserts:
            - connection is successful.
            - `disks` and `disk_speeds` are present in the message.
        """
        communicator = WebsocketCommunicator(DiskConsumer.as_asgi(), "ws/disks/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        try:
            response = await asyncio.wait_for(
                communicator.receive_json_from(), timeout=2
            )
            self.assertIn("disks", response)
            self.assertIn("disks_speeds", response)
        except asyncio.TimeoutError:
            self.fail("Test timed out waiting for initial disk details.")

        await communicator.disconnect()

    async def test_periodic_disk_metrics_message(self):
        """Test that the consumer sends periodic messages containing disks metrics.

        Assert:
            "disks" and "disks_speeds" are present in the message.
        """
        communicator = WebsocketCommunicator(DiskConsumer.as_asgi(), "ws/disks/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        periodic_response = await communicator.receive_json_from()
        self.assertIn("disks", periodic_response)
        self.assertIn("disks_speeds", periodic_response)

        await communicator.disconnect()

    async def test_websocket_disconnect(self):
        """Test that disconnecting from the DiskConsumer websocket does not raise an exception."""
        communicator = WebsocketCommunicator(DiskConsumer.as_asgi(), "ws/disks/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()
