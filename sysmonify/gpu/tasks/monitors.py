"""monitors.py.

This module contains classes and utilities for retrieving real-time GPU metrics.

Classes:
    - GPUMonitor:
        A class for retrieving real-time GPU stats for all GPUs installed on a system.

Examples:
    gpu_monitor = GPUMonitor()
    gpu_metrics = gpu_monitor.get_metrics()
    print(gpu_metrics)
"""

import logging

from sysmonify.core.tasks import Monitor
from gpu.tasks.utils import LSPCI, NvidiaSMI


logger = logging.getLogger(__name__)


class GPUMonitor(Monitor):
    """Monitors real-time GPU stats for all GPUs installed on a system.

    This class retrieves current utilization, temperature and power consumption stats
    for all GPUs installed on a system.

    Methods:
        get_metrics() -> dict:
            Gathers current GPU stats and returns the data in a dictionary.
    """

    def __init__(self) -> None:
        """Default initializer."""
        self._NVIDIA_SMI_HEADERS = [
            "index",
            "utilization.gpu",
            "utilization.memory",
            "memory.used",
            "power.draw",
            "temperature.gpu",
        ]

    async def get_metrics(self) -> dict:
        """Gathers real-time GPU metrics and returns the data in a dictionary.

        Retrieves GPU related stats for all GPUs installed on a system. Stats such as
        utilization, temperature, memory usage and power draw.

        Returns:
            dict: A dictionary of dictionaries with the following format:
            {
                "0": {
                    "gpu_utilization": "10 %",
                    "memory_utilization": "10 %",
                    "temperature": "43",
                    "memory_used": "894 MiB",
                    "power_draw": "5.91 W"
                },
                ...
            }
        """
        metrics = {}

        vendors = await LSPCI.get_gpu_vendors()

        if "NVIDIA" in vendors:
            nv_gpu_metrics = await NvidiaSMI.query_gpu(headers=self._NVIDIA_SMI_HEADERS)

            for gpu in nv_gpu_metrics:
                gpu_index = gpu.get("index")
                gpu_metrics = {
                    "gpu_utilization": gpu.get("utilization.gpu [%]", "0"),
                    "memory_utilization": gpu.get("utilization.memory [%]", "0"),
                    "temperature": gpu.get("temperature.gpu", "0"),
                    "memory_used": gpu.get("memory.used [MiB]", "0"),
                    "power_draw": gpu.get("power.draw [W]", "0"),
                }
                metrics[gpu_index] = gpu_metrics

        if "AMD" in vendors:
            logger.warning("AMD GPUs are currently not supported.")

        if "Intel" in vendors:
            logger.warning("Intel GPUs are currently not supported.")

        return metrics
