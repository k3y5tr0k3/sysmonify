"""Tests for gpu.tasks.monitors module."""

from unittest.mock import patch

from django.test import TestCase

from gpu.tasks.monitors import GPUMonitor


class TestGPUMonitor(TestCase):
    """Unit tests for the GPUMonitor class."""

    def setUp(self):
        """Set up GPUMonitor instance for testing."""
        self.gpu_monitor = GPUMonitor()

    @patch("gpu.tasks.monitors.LSPCI.get_gpu_vendors", return_value={"NVIDIA"})
    @patch("gpu.tasks.monitors.NvidiaSMI.query_gpu")
    async def test_get_metrics_success(self, mock_query_gpu, mock_get_gpu_vendors):
        """Test get_metrics returns expected NVIDIA GPU metrics.

        Asserts:
            - Output format is correct
            - Output values are as expected
        """
        mock_query_gpu.return_value = [
            {
                "index": "0",
                "utilization.gpu [%]": "15",
                "utilization.memory [%]": "20",
                "temperature.gpu": "55",
                "memory.used [MiB]": "1024",
                "power.draw [W]": "35",
            }
        ]

        metrics = await self.gpu_monitor.get_metrics()

        expected = {
            "0": {
                "gpu_utilization": "15",
                "memory_utilization": "20",
                "temperature": "55",
                "memory_used": "1024",
                "power_draw": "35",
            }
        }
        self.assertEqual(metrics, expected)

    @patch("gpu.tasks.monitors.LSPCI.get_gpu_vendors", return_value=set())
    async def test_get_metrics_no_gpu(self, mock_get_gpu_vendors):
        """Test get_metrics returns an empty dictionary when no GPU is detected.

        Asserts:
            Empty dictionary is returned when no GPUs are installed on the system.
        """
        metrics = await self.gpu_monitor.get_metrics()
        self.assertEqual(metrics, {})

    @patch("gpu.tasks.monitors.LSPCI.get_gpu_vendors", return_value={"AMD", "NVIDIA"})
    @patch("gpu.tasks.monitors.NvidiaSMI.query_gpu")
    async def test_get_metrics_amd_warning(self, mock_query_gpu, mock_get_gpu_vendors):
        """Test get_metrics logs a warning when AMD GPUs are present.

        Asserts:
            NVIDIA metrics are processed, a warning for AMD GPUs should be logged.
        """
        mock_query_gpu.return_value = [
            {
                "index": "0",
                "utilization.gpu [%]": "10",
                "utilization.memory [%]": "15",
                "temperature.gpu": "50",
                "memory.used [MiB]": "512",
                "power.draw [W]": "30",
            }
        ]

        with self.assertLogs("gpu.tasks.monitors", level="WARNING") as log_capture:
            metrics = await self.gpu_monitor.get_metrics()

        self.assertTrue(
            any(
                "AMD GPUs are currently not supported." in message
                for message in log_capture.output
            )
        )
        expected = {
            "0": {
                "gpu_utilization": "10",
                "memory_utilization": "15",
                "temperature": "50",
                "memory_used": "512",
                "power_draw": "30",
            }
        }
        self.assertEqual(metrics, expected)

    @patch("gpu.tasks.monitors.LSPCI.get_gpu_vendors", return_value={"Intel", "NVIDIA"})
    @patch("gpu.tasks.monitors.NvidiaSMI.query_gpu")
    async def test_get_metrics_intel_warning(
        self, mock_query_gpu, mock_get_gpu_vendors
    ):
        """Test get_metrics logs a warning when Intel GPUs are present.

        Asserts:
            NVIDIA metrics are processed, a warning for Intel GPUs should be logged.
        """
        mock_query_gpu.return_value = [
            {
                "index": "0",
                "utilization.gpu [%]": "20",
                "utilization.memory [%]": "25",
                "temperature.gpu": "60",
                "memory.used [MiB]": "2048",
                "power.draw [W]": "40",
            }
        ]

        with self.assertLogs("gpu.tasks.monitors", level="WARNING") as log_capture:
            metrics = await self.gpu_monitor.get_metrics()

        self.assertTrue(
            any(
                "Intel GPUs are currently not supported." in message
                for message in log_capture.output
            )
        )
        expected = {
            "0": {
                "gpu_utilization": "20",
                "memory_utilization": "25",
                "temperature": "60",
                "memory_used": "2048",
                "power_draw": "40",
            }
        }
        self.assertEqual(metrics, expected)
