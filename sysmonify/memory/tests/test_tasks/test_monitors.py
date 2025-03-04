"""Unit tests for memory app monitors."""

from unittest.mock import mock_open, patch

from django.test import TestCase
from memory.tasks.monitors import MemoryMonitor


class MemoryMonitorTestCase(TestCase):
    """Test case for MemoryMonitor."""

    @patch(
        "builtins.open",
        mock_open(
            read_data="MemTotal: 16384 kB\nMemFree: 4096 kB\nSwapTotal: 8192 kB\nSwapFree: 2048 kB"
        ),
    )
    def test_get_metrics_success(self):
        """Test that get_metrics returns correct data from /proc/meminfo.

        Assets:
            get_metrics() returns the expected values.
        """
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["memory"]["total"], 16384)
        self.assertEqual(result["memory"]["free"], 4096)
        self.assertEqual(result["swap"]["total"], 8192)
        self.assertEqual(result["swap"]["free"], 2048)

    @patch(
        "builtins.open",
        mock_open(read_data="MemTotal: 16384 kB\nMemFree: 4096 kB\nSwapTotal: 8192 kB"),
    )
    def test_get_metrics_missing_swap(self):
        """Test case where SwapFree is missing.

        Asserts:
            The default free swap value is returned.
        """
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["swap"]["free"], 0)

    @patch(
        "builtins.open",
        mock_open(read_data="MemTotal: 16384 kB\nMemFree: 4096 kB\nSwapFree: 2048 kB"),
    )
    def test_get_metrics_missing_swap_total(self):
        """Test case where SwapTotal is missing.

        Asserts:
            The default total swap value is returned.
        """
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["swap"]["total"], 0)

    @patch("builtins.open", mock_open(read_data="MemTotal: 16384 kB\nMemFree: 4096 kB"))
    def test_get_metrics_no_swap(self):
        """Test case where both swap metrics are missing.

        Asserts:
            The default values for both swap metrics is returned.
        """
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["swap"]["total"], 0)
        self.assertEqual(result["swap"]["free"], 0)

    @patch("builtins.open", mock_open(read_data=""))
    def test_get_metrics_empty_file(self):
        """Test case where /proc/meminfo is empty.

        Asserts:
            The default values for all memory metrics are returned.
        """
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["memory"]["total"], 0)
        self.assertEqual(result["memory"]["free"], 0)
        self.assertEqual(result["swap"]["total"], 0)
        self.assertEqual(result["swap"]["free"], 0)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_metrics_file_not_found(self, mock_open):
        """Test case where /proc/meminfo is not found.

        Asserts:
            - The correct error is logged.
            - The default values for all memory metrics are returned.
        """
        with self.assertLogs("memory.tasks.monitors", level="ERROR") as log_capture:
            monitor = MemoryMonitor()
            result = monitor.get_metrics()

        self.assertTrue(
            any(
                "/proc/meminfo file not found." in message
                for message in log_capture.output
            )
        )

        self.assertEqual(result["memory"]["total"], 0)
        self.assertEqual(result["memory"]["free"], 0)
        self.assertEqual(result["swap"]["total"], 0)
        self.assertEqual(result["swap"]["free"], 0)
