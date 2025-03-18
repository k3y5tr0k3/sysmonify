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
        Top, "get_processes", return_value={1234: {"COMMAND+": "python3", "CPU%": 5.0}}
    )
    async def test_get_metrics_success(self, mock_get_processes):
        """Test that get_metrics successfully retrieves process data."""
        monitor = ProcessMonitor()
        metrics = await monitor.get_metrics()

        self.assertEqual(metrics[1234]["command"], "python3")
        self.assertEqual(metrics[1234]["cpu"], 5.0)
        mock_get_processes.assert_called_once()

    @patch.object(Top, "get_processes", return_value={})
    async def test_get_metrics_failure(self, mock_get_processes):
        """Test that get_metrics handles exceptions and returns an empty dictionary."""
        monitor = ProcessMonitor()

        result = await monitor.get_metrics()
        self.assertEqual(result, {})
        mock_get_processes.assert_called_once()
