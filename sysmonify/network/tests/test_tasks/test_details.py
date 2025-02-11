"""Unit test for network details task."""

import unittest

from django.test import TestCase

from network.tasks.details import NetworkDetails


class TestNetworkDetails(TestCase):
    """Unit tests for the NetworkDetails class."""

    def setUp(self):
        """Set up a NetworkDetails instance for testing."""
        self.network_details = NetworkDetails()

    @unittest.mock.patch(
        "builtins.open",
        new_callable=unittest.mock.mock_open,
        read_data="00:11:22:33:44:55",
    )
    @unittest.mock.patch("os.path.exists", return_value=True)
    def test_get_interface_mac(self, mock_exists, mock_open_file):
        """Test retrieval of MAC address from a system file.

        Asserts:
            Expected MAC address is returned.
        """
        mac_address = self.network_details._get_interface_mac("eth0")
        self.assertEqual(mac_address, "00:11:22:33:44:55")

    @unittest.mock.patch(
        "builtins.open", new_callable=unittest.mock.mock_open, read_data="1500"
    )
    @unittest.mock.patch("os.path.exists", return_value=True)
    def test_get_interface_mtu(self, mock_exists, mock_open_file):
        """Test retrieval of MTU from a system file.

        Asserts:
            Expected MTU is returned.
        """
        mtu = self.network_details._get_interface_mtu("eth0")
        self.assertEqual(mtu, "1500")

    @unittest.mock.patch(
        "builtins.open", new_callable=unittest.mock.mock_open, read_data="1000"
    )
    @unittest.mock.patch("os.path.exists", return_value=True)
    def test_get_interface_max_speed(self, mock_exists, mock_open_file):
        """Test retrieval of max link speed from a system file.

        Asserts:
            Expected speed is returned.
        """
        speed = self.network_details._get_interface_max_speed("eth0")
        self.assertEqual(speed, "1000")

    @unittest.mock.patch(
        "builtins.open",
        new_callable=unittest.mock.mock_open,
        read_data="DEVTYPE=wlan\n",
    )
    @unittest.mock.patch("os.path.exists", return_value=True)
    def test_get_interface_type_wifi(self, mock_exists, mock_open_file):
        """Test retrieving interface type when it is a WiFi interface.

        Asserts:
            Expected interface type is returned.
        """
        interface_type = self.network_details._get_interface_type("wlan0")
        self.assertEqual(interface_type, "WiFi")

    @unittest.mock.patch(
        "builtins.open", new_callable=unittest.mock.mock_open, read_data=""
    )
    @unittest.mock.patch("os.path.exists", return_value=True)
    def test_get_interface_type_ethernet(self, mock_exists, mock_open_file):
        """Test retrieving interface type when it is an Ethernet interface.

        Asserts:
            Expected interface type is returned.
        """
        interface_type = self.network_details._get_interface_type("eth0")
        self.assertEqual(interface_type, "Ethernet")

    @unittest.mock.patch(
        "network.tasks.details.get_physical_network_interfaces", return_value=["eth0"]
    )
    @unittest.mock.patch(
        "network.tasks.details.NetworkDetails._get_interface_mac",
        return_value="00:11:22:33:44:55",
    )
    @unittest.mock.patch(
        "network.tasks.details.NetworkDetails._get_interface_mtu", return_value="1500"
    )
    @unittest.mock.patch(
        "network.tasks.details.NetworkDetails._get_interface_max_speed",
        return_value="1000",
    )
    @unittest.mock.patch(
        "network.tasks.details.NetworkDetails._get_interface_type",
        return_value="Ethernet",
    )
    @unittest.mock.patch(
        "network.tasks.utils.IP.get_ip_addresses", new_callable=unittest.mock.AsyncMock
    )
    async def test_get_details(
        self,
        mock_get_ips,
        mock_get_type,
        mock_get_speed,
        mock_get_mtu,
        mock_get_mac,
        mock_get_interfaces,
    ):
        """Test retrieval of complete network details.

        Asserts:
            The details dictionary contains the expected keys, and each value is as
            expected.
        """
        mock_get_ips.side_effect = [["192.168.1.1"], ["fe80::1"]]

        details = await self.network_details.get_details()

        self.assertIn("eth0", details)
        self.assertIn("mac", details["eth0"])
        self.assertEqual(details["eth0"]["mac"], "00:11:22:33:44:55")
        self.assertIn("type", details["eth0"])
        self.assertEqual(details["eth0"]["type"], "Ethernet")
        self.assertIn("mtu", details["eth0"])
        self.assertEqual(details["eth0"]["mtu"], "1500")
        self.assertIn("speed", details["eth0"])
        self.assertEqual(details["eth0"]["speed"], "1000")
        self.assertIn("ipv4", details["eth0"])
        self.assertEqual(details["eth0"]["ipv4"], ["192.168.1.1"])
        self.assertIn("ipv6", details["eth0"])
        self.assertEqual(details["eth0"]["ipv6"], ["fe80::1"])

    @unittest.mock.patch("os.path.exists", return_value=False)
    def test_get_interface_mac_error_returns_default(self, mock_exists):
        """Test error handling in MAC address retrieval.

        Assert:
            Default MAC address is returned.
        """
        mac = self.network_details._get_interface_mac("eth0")
        self.assertEqual(mac, "Unknown")

    @unittest.mock.patch("os.path.exists", return_value=False)
    def test_get_interface_mtu_error(self, mock_exists):
        """Test error handling in MTU retrieval.

        Asserts:
            Default MTU is returned.
        """
        mtu = self.network_details._get_interface_mtu("eth0")
        self.assertEqual(mtu, "Unknown")

    @unittest.mock.patch("os.path.exists", return_value=False)
    def test_get_interface_max_speed_error(self, mock_exists):
        """Test error handling in max speed retrieval.

        Asserts:
            Default speed is returned.
        """
        speed = self.network_details._get_interface_max_speed("eth0")

        self.assertEqual(speed, "Unknown")

    @unittest.mock.patch("os.path.exists", return_value=False)
    def test_get_interface_type_error(self, mock_exists):
        """Test error handling in interface type retrieval.

        Assert:
            Default interface type is returned.
        """
        interface_type = self.network_details._get_interface_type("eth0")

        self.assertEqual(interface_type, "Ethernet")
