"""details.py.

A module for retrieving detailed GPU details such as vendor, model, vram and more.

Classes:
    GPUDetails:
        A class for retrieving GPU details such as vendor, model, vram and more.
"""

import logging

from sysmonify.core.tasks import Details
from gpu.tasks.utils import NvidiaSMI, LSPCI


logger = logging.getLogger(__name__)


class GPUDetails(Details):
    """A class for retrieving GPU details such as vendor, model, vram and more.

    Example:
            gpu_details = GPUDetails()
            gpu_info = gpu_details.get_details()
            print(gpu_info[0]['vendor'])  # Output: 'NVIDIA'
            print(gpu_info[0]['min_power'])   # Output: '5.00'
    """

    def __init__(self) -> None:
        """Default initializer."""
        self._NVIDIA_SMI_HEADERS = [
            "index",
            "gpu_name",
            "uuid",
            "driver_version",
            "memory.total",
            "power.max_limit",
            "power.min_limit",
        ]

    async def get_details(self) -> dict:
        """Gather details about all GPUs on the system and return the details in a dictionary.

        Gathers a list of GPU details, for GPUs installed in the system, and then use
        vendor specific subprocesses to gather details for each GPU.

        This method returns key details about the system's CPU, including:
        - Index (e.g., 0)
        - Vendor (e.g., NVIDIA, AMD)
        - Model (e.g., NVIDIA GeForce RTX™ 4050 Laptop GPU)
        - UUID (e.g., GPU-c6fd5115-f7fc-73ba-4862-000000000)
        - Total VRAM (e.g., 6141)
        - Driver version (e.g., 550.107.02)
        - Min Power (e.g., 5.00)
        - Max Power (e.g., 50.00)

        Returns:
            dict: A dictionary of dictionaries with the following format:
            {
                "0": {
                    "vendor": "NVIDIA",
                    "model": "NVIDIA GeForce RTX™ 4050 Laptop GPU",
                    ...
                },
                "1": {...},
                ...
            }

        Note:
            Some details may not be available on all systems. The method will try to
            fetch as much information as possible, but results may vary depending on
            the platform and the GPU driver capabilities.
        """
        details = {}
        vendors = await LSPCI.get_gpu_vendors()

        if "NVIDIA" in vendors:
            nv_gpu_details = await NvidiaSMI.query_gpu(headers=self._NVIDIA_SMI_HEADERS)

            for gpu in nv_gpu_details:
                gpu_index = gpu.get("index")
                gpu_details = {
                    "vendor": "NVIDIA Corporation",
                    "model": gpu.get("name", "Unknown"),
                    "uuid": gpu.get("uuid", "Unknown"),
                    "total_vram": gpu.get("memory.total [MiB]", "Unknown"),
                    "driver_version": gpu.get("driver_version", "Unknown"),
                    "min_power": gpu.get("power.min_limit [W]", "Unknown"),
                    "max_power": gpu.get("power.max_limit [W]", "Unknown"),
                }
                details[gpu_index] = gpu_details

        if "AMD" in vendors:
            logger.warning("AMD GPUs are currently not supported.")

        if "Intel" in vendors:
            logger.warning("Intel GPUs are currently not supported.")

        return details
