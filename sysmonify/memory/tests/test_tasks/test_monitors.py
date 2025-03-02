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
        """Test that get_metrics returns correct data from /proc/meminfo."""
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["memory"]["total"], "16384 kB")
        self.assertEqual(result["memory"]["free"], "4096 kB")
        self.assertEqual(result["swap"]["total"], "8192 kB")
        self.assertEqual(result["swap"]["free"], "2048 kB")

    @patch(
        "builtins.open",
        mock_open(read_data="MemTotal: 16384 kB\nMemFree: 4096 kB\nSwapTotal: 8192 kB"),
    )
    def test_get_metrics_missing_swap(self):
        """Test case where SwapFree is missing."""
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["swap"]["free"], "0 KB")

    @patch(
        "builtins.open",
        mock_open(read_data="MemTotal: 16384 kB\nMemFree: 4096 kB\nSwapFree: 2048 kB"),
    )
    def test_get_metrics_missing_swap_total(self):
        """Test case where SwapTotal is missing."""
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["swap"]["total"], "0 KB")

    @patch("builtins.open", mock_open(read_data="MemTotal: 16384 kB\nMemFree: 4096 kB"))
    def test_get_metrics_no_swap(self):
        """Test case where both swap metrics are missing."""
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["swap"]["total"], "0 KB")
        self.assertEqual(result["swap"]["free"], "0 KB")

    @patch("builtins.open", mock_open(read_data=""))
    def test_get_metrics_empty_file(self):
        """Test case where /proc/meminfo is empty."""
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["memory"]["total"], "0 KB")
        self.assertEqual(result["memory"]["free"], "0 KB")
        self.assertEqual(result["swap"]["total"], "0 KB")
        self.assertEqual(result["swap"]["free"], "0 KB")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_metrics_file_not_found(self, mock_open):
        """Test case where /proc/meminfo is not found."""
        monitor = MemoryMonitor()
        result = monitor.get_metrics()

        self.assertEqual(result["memory"]["total"], "0 KB")
        self.assertEqual(result["memory"]["free"], "0 KB")
        self.assertEqual(result["swap"]["total"], "0 KB")
        self.assertEqual(result["swap"]["free"], "0 KB")
