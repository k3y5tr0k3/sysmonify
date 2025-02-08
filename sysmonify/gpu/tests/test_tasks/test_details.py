"""Unit tests for gpu.tasks.details module."""

import unittest

from django.test import TestCase

from gpu.tasks.details import GPUDetails


class TestGPUDetails(TestCase):
    """Unit tests for GPUDetails class."""

    def setUp(self):
        """Set up GPUDetails instance for testing."""
        self.gpu_details = GPUDetails()

    @unittest.mock.patch(
        "gpu.tasks.details.LSPCI.get_gpu_vendors", return_value={"NVIDIA"}
    )
    @unittest.mock.patch("gpu.tasks.details.NvidiaSMI.query_gpu")
    async def test_get_details_nvidia(self, mock_nvidia_smi, mock_lspci):
        """Test get_details returns expected NVIDIA GPU details.

        Asserts:
            - The details are returned in a dictionary with GPU index keys.
            - The values for vendor, model, and total_vram match expected values.
        """
        mock_nvidia_smi.return_value = [
            {
                "index": "0",
                "name": "NVIDIA GeForce RTX 4050",
                "uuid": "GPU-123456",
                "driver_version": "550.107.02",
                "memory.total [MiB]": "6144 MiB",
                "power.max_limit [W]": "50.00 W",
                "power.min_limit [W]": "5.00 W",
            }
        ]

        details = await self.gpu_details.get_details()

        # Assert that details is a dictionary and contains a key for GPU index "0"
        self.assertIsInstance(details, dict)
        self.assertIn("0", details)
        gpu_detail = details["0"]
        self.assertEqual(gpu_detail["vendor"], "NVIDIA Corporation")
        self.assertEqual(gpu_detail["model"], "NVIDIA GeForce RTX 4050")
        self.assertEqual(gpu_detail["total_vram"], "6144 MiB")

    @unittest.mock.patch("gpu.tasks.details.LSPCI.get_gpu_vendors", return_value=set())
    async def test_get_details_no_gpu(self, mock_lspci):
        """Test get_details when no GPU is detected.

        Asserts:
            LSPCI returns an empty set if no GPUs are installed on the system.
        """
        details = await self.gpu_details.get_details()
        self.assertEqual(details, {})
