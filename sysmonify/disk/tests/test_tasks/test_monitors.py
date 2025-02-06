"""test_monitors.py.

Test cases for disk.tests.monitors
"""

import datetime
import unittest

from disk.tasks.monitors import DiskIOMonitor


class TestDiskIOMonitor(unittest.TestCase):
    """Test case for DiskIO Monitor.

    Tests:
        - test_get_metrics:
            returns expected output.

        - test_sectors_to_megabytes:
            correctly converts disk sector value to megabyte equivalent.
    """

    def setUp(self):
        """Test case setup.

        Creates:
            - list of disks.
            - mock object for mocking `_get_current_sectors` method.
        """
        self.disks = ["sda", "nvme0n1"]
        patcher = unittest.mock.patch.object(
            DiskIOMonitor,
            "_get_current_disks_sectors",
            return_value={
                "sda": {"read": 0, "written": 0},
                "nvme0n1": {"read": 0, "written": 0},
            },
        )
        self.addCleanup(patcher.stop)
        self.mock_init_sectors = patcher.start()

        self.monitor = DiskIOMonitor(disks=self.disks)

    @unittest.mock.patch(
        "disk.tasks.monitors.datetime.datetime", wraps=datetime.datetime
    )
    @unittest.mock.patch.object(
        DiskIOMonitor,
        "_get_current_disks_sectors",
        return_value={
            "sda": {"read": 1024, "written": 4096},
            "nvme0n1": {"read": 2048, "written": 8192},
        },
    )
    def test_get_metrics(self, mock_get_sectors, mock_datetime):
        """Test get metrics.

        Asserts:
            - Return value contains all expected keys (disk names).
            - Each disk has `read_speed` and `write_speed` keys.
            - `read_speed` and `write_speed` are of type `float`
        """
        self.monitor._previous_timestamp = datetime.datetime(2024, 2, 5, 12, 0, 0)
        self.monitor._previous_disks_sectors = {
            "sda": {"read": 0, "written": 0},
            "nvme0n1": {"read": 0, "written": 0},
        }
        mock_datetime.now.side_effect = [
            datetime.datetime(2024, 2, 5, 12, 0, 1),
        ]

        metrics = self.monitor.get_metrics()

        expected_metrics = {
            "sda": {"read_speed": unittest.mock.ANY, "write_speed": unittest.mock.ANY},
            "nvme0n1": {
                "read_speed": unittest.mock.ANY,
                "write_speed": unittest.mock.ANY,
            },
        }

        self.assertEqual(set(metrics.keys()), set(expected_metrics.keys()))
        for disk in expected_metrics:
            self.assertIn("read_speed", metrics[disk])
            self.assertIn("write_speed", metrics[disk])
            self.assertIsInstance(metrics[disk]["read_speed"], float)
            self.assertIsInstance(metrics[disk]["write_speed"], float)

    def test_sectors_to_megabytes(self):
        """Test that sectors can be converted to megabytes.

        Asserts:
            Sectors are correctly converted to megabytes.
        """
        self.assertEqual(self.monitor._sectors_to_megabytes(2048), 1)
        self.assertEqual(self.monitor._sectors_to_megabytes(4096), 2)
