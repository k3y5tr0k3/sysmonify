"""test_details.py.

Tests for disk.tasks.details module.
"""

import asyncio
import json
import unittest

from django.test import TestCase

from disk.tasks.details import DiskDetails


class DiskDetailsTestCase(TestCase):
    """Test case for the DiskDetails class."""

    def setUp(self):
        """Initialize the test case with a DiskDetails instance."""
        self.disk_details = DiskDetails()

    @unittest.mock.patch("subprocess.run")
    def test_get_raw_block_devices_success(self, mock_subprocess):
        """Test _get_raw_block_devices when lsblk returns valid JSON data.

        Asserts:
            - A list is returned.
            - The correct number of element are present in the list.
            - The name of the first block device is what is expected.
        """
        mock_output = json.dumps(
            {
                "blockdevices": [
                    {"name": "sda", "type": "disk", "size": "500G"},
                    {"name": "sda1", "type": "part", "size": "250G"},
                ]
            }
        )
        mock_subprocess.return_value = unittest.mock.MagicMock(stdout=mock_output)

        result = self.disk_details._get_raw_block_devices()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "sda")

    @unittest.mock.patch("pathlib.Path.resolve")
    def test_is_physical_disk(self, mock_resolve):
        """Test _is_physical_disk to differentiate physical and virtual disks.

        Asserts:
            - `True` is returned for physical disks.
            - `False` is returned for virtual disks.
        """
        mock_resolve.return_value = "/sys/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda"
        self.assertTrue(self.disk_details._is_physical_disk("sda"))

        mock_resolve.return_value = "/sys/devices/virtual/block/zd0"
        self.assertFalse(self.disk_details._is_physical_disk("zd0"))

    def test_get_physical_disks_from_raw_block_devices(self):
        """Test filtering physical disks from block devices.

        Asserts:
            - disks that should be filtered out are removed (e.g. loopback devices).
            - disks that should remain are present in return value (e.g. disks).
        """
        raw_devices = [
            {"name": "sda", "type": "disk"},
            {"name": "sdb", "type": "disk"},
            {"name": "loop0", "type": "loop"},
        ]

        with unittest.mock.patch.object(
            self.disk_details,
            "_is_physical_disk",
            side_effect=lambda block_device_name: block_device_name != "loop0",
        ):
            physical_disks = (
                self.disk_details._get_physical_disks_from_raw_block_devices(
                    raw_devices
                )
            )

            self.assertEqual(len(physical_disks), 2)
            self.assertEqual(physical_disks[0]["name"], "sda")
            self.assertEqual(physical_disks[1]["name"], "sdb")

    @unittest.mock.patch.object(DiskDetails, "_get_raw_block_devices")
    @unittest.mock.patch.object(
        DiskDetails, "_get_physical_disks_from_raw_block_devices"
    )
    def test_get_details(self, mock_get_physical, mock_get_raw):
        """Test get_details method to ensure it returns filtered physical disks.

        Asserts:
            Only details of physical disks are returned.
        """
        mock_get_raw.return_value = [
            {"name": "sda", "type": "disk"},
            {"name": "sda1", "type": "part"},
        ]
        mock_get_physical.return_value = [{"name": "sda", "type": "disk"}]

        details = asyncio.run(self.disk_details.get_details())
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]["name"], "sda")
