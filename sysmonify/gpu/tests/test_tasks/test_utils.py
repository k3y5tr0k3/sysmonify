"""Tests for gpu.tasks.utils module."""

import unittest

from django.test import TestCase

from gpu.tasks.utils import NvidiaSMI, LSPCI


class TestNvidiaSMI(TestCase):
    """Unit tests for NvidiaSMI utility class."""

    @unittest.mock.patch("gpu.tasks.utils.run_command_async")
    async def test_query_gpu_success(self, mock_run_command_async):
        """Test query_gpu returns expected GPU info.

        Asserts:
            - Expected number of GPU detail dictionaries is present in the list
            - GPU detail values are as expected.
        """
        mock_run_command_async.return_value = {
            "exit_code": 0,
            "stdout": "index, gpu_name, uuid, driver_version, memory.total, power.max_limit, power.min_limit\n"
            "0, NVIDIA GeForce RTX 4050, GPU-123456, 550.107.02, 6144, 50.00, 5.00\n",
            "stderr": "",
        }

        headers = [
            "index",
            "gpu_name",
            "uuid",
            "driver_version",
            "memory.total",
            "power.max_limit",
            "power.min_limit",
        ]
        gpu_info = await NvidiaSMI.query_gpu(headers)

        self.assertEqual(len(gpu_info), 1)
        self.assertEqual(gpu_info[0]["index"], "0")
        self.assertEqual(gpu_info[0]["gpu_name"], "NVIDIA GeForce RTX 4050")
        self.assertEqual(gpu_info[0]["uuid"], "GPU-123456")
        self.assertEqual(gpu_info[0]["driver_version"], "550.107.02")
        self.assertEqual(gpu_info[0]["memory.total"], "6144")

    @unittest.mock.patch("gpu.tasks.utils.run_command_async")
    async def test_query_gpu_failure(self, mock_run_command_async):
        """Test query_gpu handles error when nvidia-smi fails.

        Asserts:
            - An empty list is returned.
            - The expected error message is logged.
        """
        mock_run_command_async.return_value = {
            "exit_code": 1,
            "stdout": "",
            "stderr": "Error: nvidia-smi command failed",
        }

        headers = [
            "index",
            "gpu_name",
            "uuid",
            "driver_version",
            "memory.total",
            "power.max_limit",
            "power.min_limit",
        ]

        with self.assertLogs("gpu.tasks.utils", level="ERROR") as log_capture:
            gpu_info = await NvidiaSMI.query_gpu(headers)

        self.assertEqual(gpu_info, [])
        self.assertTrue(
            any(
                "Error occurred when running 'nvidia-smi'" in message
                for message in log_capture.output
            )
        )


class TestLSPCI(TestCase):
    """Unit tests for LSPCI utility class."""

    @unittest.mock.patch("gpu.tasks.utils.run_command_async")
    async def test_get_gpu_vendors_success(self, mock_run_command_async):
        """Test get_gpu_vendors detects GPU vendors correctly.

        Asserts:
            - The correct GPU vendor are returned based on 'lspci' output.
        """
        mock_run_command_async.return_value = {
            "exit_code": 0,
            "stdout": "00:02.0 VGA compatible controller: Intel Corporation Device [9101]\n"
            "01:00.0 VGA compatible controller: NVIDIA Corporation Device [1234]\n"
            "02:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Device [5678]\n",
            "stderr": "",
        }

        gpu_vendors = await LSPCI.get_gpu_vendors()

        self.assertIn("NVIDIA", gpu_vendors)
        self.assertIn("AMD", gpu_vendors)
        self.assertIn("Intel", gpu_vendors)

    @unittest.mock.patch("gpu.tasks.utils.run_command_async")
    async def test_get_gpu_vendors_failure(self, mock_run_command_async):
        """Test get_gpu_vendors handles failure when lspci fails.

        Asserts:
            - An empty set is return.
            - The expected error message is logged.
        """
        mock_run_command_async.return_value = {
            "exit_code": 1,
            "stdout": "",
            "stderr": "Error: lspci command failed",
        }

        with self.assertLogs("gpu.tasks.utils", level="ERROR") as log_capture:
            gpu_vendors = await LSPCI.get_gpu_vendors()

        self.assertEqual(gpu_vendors, set())
        self.assertTrue(
            any(
                "Unexpected error occurred when querying lspci for available GPUs"
                in message
                for message in log_capture.output
            )
        )

    @unittest.mock.patch("gpu.tasks.utils.run_command_async")
    async def test_get_gpu_vendors_empty(self, mock_run_command_async):
        """Test get_gpu_vendors handles empty output from lspci.

        Asserts:
            An empty set is returned when no GPUs are installed in the system.
        """
        mock_run_command_async.return_value = {
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        }

        gpu_vendors = await LSPCI.get_gpu_vendors()

        self.assertEqual(gpu_vendors, set())
