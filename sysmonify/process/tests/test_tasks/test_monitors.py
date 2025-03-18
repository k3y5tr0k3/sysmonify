"""test_monitors.py.

Unit test for process monitors.
"""

from unittest.mock import patch

from django.test import TestCase
from process.tasks.monitors import ProcessMonitor
from process.tasks.utils import Top


class TestProcessMonitor(TestCase):
    """Unit tests for the ProcessMonitor class."""

    @patch.object(
        Top, "get_processes", return_value={1234: {"COMMAND": "python3", "CPU%": 5.0}}
    )
    async def test_get_metrics_success(self, mock_get_processes):
        """Test that get_metrics successfully retrieves process data."""
        monitor = ProcessMonitor()
        metrics = await monitor.get_metrics()

        expected_output = {1234: {"COMMAND": "python3", "CPU%": 5.0}}

        self.assertEqual(metrics, expected_output)
        mock_get_processes.assert_called_once()

    @patch.object(Top, "get_processes", side_effect=Exception("Top command failed"))
    async def test_get_metrics_failure(self, mock_get_processes):
        """Test that get_metrics handles exceptions and returns an empty dictionary."""
        monitor = ProcessMonitor()
        metrics = await monitor.get_metrics()

        self.assertEqual(metrics, {})
        mock_get_processes.assert_called_once()
