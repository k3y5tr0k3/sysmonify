"""Unit tests for network monitor tasks."""

import unittest
import datetime

from django.test import TestCase

from network.tasks.monitors import NetworkStatsMonitor


class TestNetworkStatsMonitor(TestCase):
    """Unit tests for the NetworkStatsMonitor class."""

    def setUp(self):
        """Set up a NetworkMonitor instance for testing."""
        self.net_stat_monitor = NetworkStatsMonitor()

    @unittest.mock.patch(
        "network.tasks.monitors.get_physical_network_interfaces", return_value=["eth0"]
    )
    @unittest.mock.patch(
        "network.tasks.utils.IP.get_interface_stats",
        new_callable=unittest.mock.AsyncMock,
    )
    async def test_get_metrics(self, mock_get_stats, mock_get_interfaces):
        """Test that get_metrics returns correct Mbps rates and dropped packets for an interface.

        Asserts:
            - The metric dictionary contains the expected keys.
            - Values are as expected.
        """
        self.net_stat_monitor._previous_network_stats = {
            "eth0": {
                "rx": {"bytes": 1000000, "dropped": 5},
                "tx": {"bytes": 500000, "dropped": 2},
            }
        }
        self.net_stat_monitor._previous_timestamp = (
            datetime.datetime.now() - datetime.timedelta(seconds=10)
        )

        mock_get_stats.return_value = {
            "rx": {"bytes": 2000000, "dropped": 7},
            "tx": {"bytes": 600000, "dropped": 2},
        }

        metrics = await self.net_stat_monitor.get_metrics()

        expected_rx_mbps = (1000000 / 1048576) / 10
        expected_tx_mbps = (100000 / 1048576) / 10

        self.assertIn("eth0", metrics)
        self.assertIn("rx_mbps", metrics["eth0"])
        self.assertAlmostEqual(metrics["eth0"]["rx_mbps"], expected_rx_mbps, places=3)
        self.assertIn("tx_mbps", metrics["eth0"])
        self.assertAlmostEqual(metrics["eth0"]["tx_mbps"], expected_tx_mbps, places=3)
        self.assertEqual(metrics["eth0"]["rx_dropped"], 2)
        self.assertIn("rx_dropped", metrics["eth0"])
        self.assertEqual(metrics["eth0"]["tx_dropped"], 0)
        self.assertIn("tx_dropped", metrics["eth0"])
