"""Unit tests for network monitor tasks."""

import pathlib
import socket
import unittest
import datetime

from django.test import TestCase

from network.tasks.monitors import NetworkStatsMonitor, NetworkConnectionsMonitor


class TestNetworkStatsMonitor(TestCase):
    """Unit tests for the NetworkStatsMonitor class."""

    def setUp(self):
        """Set up a NetworkStatsMonitor instance for testing."""
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


class TestNetworkConnectionsMonitor(unittest.TestCase):
    """Unit tests for NetworkConnectionsMonitor class."""

    def setUp(self):
        """Setup NetworkConnectionMonitor and define some sample data."""
        self.net_con_monitor = NetworkConnectionsMonitor()
        self.valid_tcp_data = """
            0: 0100007F:1F90 00000000:0000 01 00000000:00000000 00:00000000 00000000   1000 0 12345
        """
        self.valid_tcp6_data = """
            0: 00000000000000000000000000000001:1F90 00000000000000000000000000000000:0000 01 00000000:00000000 00:00000000 00000000   1000 0 67890
        """
        self.inode_proc_mock = {
            "12345": (1234, "test_process"),
            "67890": (5678, "test_process6"),
        }

    @unittest.mock.patch(
        "network.tasks.monitors.NetworkConnectionsMonitor._get_socket_process_map"
    )
    @unittest.mock.patch(
        "network.tasks.monitors.NetworkConnectionsMonitor._parse_proc_net_file"
    )
    def test_get_metrics(self, mock_proc_net, mock_proc_map):
        """Test the get_metrics() method to ensure that it processes the network connections correctly.

        Asserts:
            The output is the correct format and contains expected values.
        """
        mock_proc_map.return_value = {
            "459876": ("1234", "process_1"),
            "512387": ("5678", "process_2"),
        }

        mock_proc_net.return_value = [
            {
                "pid": "1234",
                "process": "process_1",
                "protocol": "UDP",
                "state": "N/A",
                "local_address": "[::]:1716",
                "foreign_address": "[::]:0",
                "send_bytes": 0,
                "received_bytes": 0,
                "inode": "459876",
            },
            {
                "pid": "5678",
                "process": "process_2",
                "protocol": "TCP",
                "state": "ESTABLISHED",
                "local_address": "[::]:1716",
                "foreign_address": "[::]:0",
                "send_bytes": 0,
                "received_bytes": 0,
                "inode": "512387",
            },
        ]

        result = self.net_con_monitor.get_metrics()

        self.assertEqual(len(result), 2)

        connection = list(result.values())[0]

        self.assertEqual(connection["protocol"], "UDP")
        self.assertEqual(connection["state"], "N/A")
        self.assertEqual(connection["local_address"], "[::]:1716")
        self.assertEqual(connection["foreign_address"], "[::]:0")
        self.assertEqual(connection["send_bytes"], 0)
        self.assertEqual(connection["received_bytes"], 0)
        self.assertEqual(connection["pid"], "1234")
        self.assertEqual(connection["process"], "process_1")

    @unittest.mock.patch("os.listdir")
    @unittest.mock.patch("os.readlink")
    def test_parse_address_ipv4(self, mock_readlink, mock_listdir):
        """Test the parsing of IPv4 addresses from hexadecimal to human-readable format.

        Asserts:
            Hexadecimal IP and port are correctly parsed to human readable IPv4 with
            format IP:PORT
        """
        hex_ip = "0100007F"
        hex_port = "1F90"
        family = socket.AF_INET

        result = self.net_con_monitor._parse_address(
            hex_ip=hex_ip, hex_port=hex_port, family=family
        )

        self.assertEqual(result, "127.0.0.1:8080")

    @unittest.mock.patch("os.listdir")
    @unittest.mock.patch("os.readlink")
    def test_parse_address_ipv6(self, mock_readlink, mock_listdir):
        """Test the parsing of IPv6 addresses from hexadecimal to human-readable format.

        Asserts:
            Hexadecimal IP and port are correctly parsed to human readable IPv6 with
            format IP:PORT
        """
        hex_ip = "00000000000000000000000000000001"
        hex_port = "1F90"
        family = socket.AF_INET6

        result = self.net_con_monitor._parse_address(
            hex_ip=hex_ip, hex_port=hex_port, family=family
        )

        self.assertEqual(result, "[::1]:8080")

    @unittest.mock.patch.object(NetworkConnectionsMonitor, "_parse_address")
    @unittest.mock.patch.object(NetworkConnectionsMonitor, "_get_process_path")
    def test_valid_tcp_parsing(self, mock_get_process_path, mock_parse_address):
        """Test successful parsing of a valid TCP entry.

        Asserts:
            Correctly parsing of /proc/net/ files.
        """
        mock_parse_address.return_value = "127.0.0.1:8080"
        mock_get_process_path.return_value = "/proc/1234/exe"

        with unittest.mock.patch(
            "builtins.open", unittest.mock.mock_open(read_data=self.valid_tcp_data)
        ):
            result = self.net_con_monitor._parse_proc_net_file(
                pathlib.Path("/proc/net/tcp"),
                "tcp",
                socket.AF_INET,
                self.inode_proc_mock,
            )

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["pid"], 1234)
            self.assertEqual(result[0]["process"], "test_process")
            self.assertEqual(result[0]["process_path"], "/proc/1234/exe")
            self.assertEqual(result[0]["protocol"], "TCP")
            self.assertEqual(result[0]["state"], "ESTABLISHED")
            self.assertEqual(result[0]["local_address"], "127.0.0.1:8080")
            self.assertEqual(result[0]["foreign_address"], "127.0.0.1:8080")
            self.assertEqual(result[0]["send_bytes"], 0)
            self.assertEqual(result[0]["received_bytes"], 0)

    @unittest.mock.patch("os.listdir")
    @unittest.mock.patch("os.readlink")
    @unittest.mock.patch(
        "builtins.open",
        new_callable=unittest.mock.mock_open,
        read_data="test_process\n",
    )
    def test_get_socket_process_map(self, mock_open_file, mock_readlink, mock_listdir):
        """Test that the method correctly maps socket inodes to process IDs and names.

        Assert:
            Inodes are correctly mapped to system processes.
        """
        mock_listdir.side_effect = [
            ["1234", "5678"],
            ["1", "2"],
            ["3", "4"],
        ]

        mock_readlink.side_effect = [
            "socket:[1111]",
            "socket:[2222]",
            "socket:[3333]",
            "socket:[4444]",
        ]

        result = self.net_con_monitor._get_socket_process_map()

        expected_result = {
            "1111": ("1234", "test_process"),
            "2222": ("1234", "test_process"),
            "3333": ("5678", "test_process"),
            "4444": ("5678", "test_process"),
        }

        self.assertEqual(result, expected_result)

        mock_open_file.assert_any_call("/proc/1234/comm", "r")
        mock_open_file.assert_any_call("/proc/5678/comm", "r")
