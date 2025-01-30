"""details.py.

This module defines the CPUDetails class, which is responsible for retrieving detailed
information about the CPU on the current system.

The class contains methods to gather various statistics related to the CPU, such as:
- Vendor and model information
- Core and thread count
- CPU architecture and other CPU features
- Cache sizes (L1, L2, L3)
- CPU min, max and turbo frequencies

The `CPUDetails` class leverages libraries like `psutil` and `cpuinfo` to query cpu
details.

Class:
    - `CPUDetails`:
        A class that provides methods to retrieve detailed information about the CPU.
"""

import logging
import subprocess

import psutil
import cpuinfo

from sysmonify.core.tasks import Details


logger = logging.getLogger(__name__)


class CPUDetails(Details):
    """A class for retrieving detailed information about the CPU of the current system.

    This class gathers a wide range of CPU-related information, such as vendor, model,
    architecture, core count, cache sizes, min/max frequencies, and more. It can be used
    to retrieve information about the CPU's capabilities.

    Attributes:
        - `_raw_cpu_info` (dict):
            A dictionary containing detailed information about the CPU, such as vendor,
            model, cache size, etc.

    Methods:
        - `get_details()`:
            Retrieves general information about the CPU, such as vendor, model,
            architecture, and core count.

        - `_get_turbo_frequency_linux()`:
            Retrieves the maximum turbo frequency of the CPU using `lscpu`.

        - `_get_cpu_cache_sizes()`:
            Retrieves and formats the CPU cache sizes from `cpuinfo`.

    Example usage:
        cpu_details = CPUDetails()
        details = cpu_details.get_details()
        print(details)

    Note:
        This class uses the `psutil` and `cpuinfo` libraries to gather system data and
        may require additional permissions or elevated privileges to access certain
        information.
    """

    def __init__(self) -> None:
        """Default initializer."""
        try:
            self._raw_cpu_info = cpuinfo.get_cpu_info()
        except Exception:
            logger.exception("Failed to retrieve raw cpu info from `cpuinfo` module.")

    async def _get_turbo_frequency_linux(self) -> float:
        """Retrieves the maximum turbo frequency of the CPU using `lscpu`.

        This method uses the `lscpu` command to query the system's BIOS and fetch
        the maximum turbo frequency supported by the CPU. The value is extracted
        from the CPU's configuration section, specifically targeting the "Max Speed"
        or similar field.

        Returns:
            float: The maximum turbo frequency of the CPU in MHz, or 0.0 if the
                information could not be retrieved.
        """
        turbo_freq = 0.0

        try:
            result = subprocess.run(["lscpu"], capture_output=True, text=True)

            for line in result.stdout.split("\n"):
                if "CPU max MHz" in line:
                    turbo_freq = float(line.split(":")[1].strip())

        except Exception:
            logger.exception(
                "Unexecuted exception occurred while invoking subprocess `lscpu`."
                "Error: {e}"
            )

        return turbo_freq

    async def _get_cpu_cache_sizes(self) -> dict:
        """Retrieves and formats the CPU cache sizes from `cpuinfo`.

        This method parses cache size information (L1, L2, L3) from the `cpuinfo` data,
        typically represented as integers in bytes.  method converts the byte values
        into kilobytes or megabytes (KB or MB) for ease of interpretation and
        standardization.

        Returns:
            dict: A dictionary containing the cache sizes with keys:
                - "l1":
                    str - Size of the L1 cache in KB (or 'Unknown' if not available).
                - "l2":
                    str - Size of the L2 cache in MB (or 'Unknown' if not available).
                - "l3":
                    str - Size of the L3 cache in MB (or 'Unknown' if not available).

        Raises:
            TypeError:
                If `psutil` returns an unexpected type when querying cpu cache sizes.
            Exception:
                If unexpected error occurs when querying cpu cache sizes.
        """
        cache_sizes = {
            "l1": "Unknown",
            "l2": "Unknown",
            "l3": "Unknown",
        }

        try:
            l1_instruction_cache = self._raw_cpu_info.get(
                "l1_instruction_cache_size", 0
            )
            l1_data_cache = self._raw_cpu_info.get("l1_data_cache_size", 0)
            if isinstance(l1_instruction_cache, int) and isinstance(l1_data_cache, int):
                total_l1_cache_kb = (l1_instruction_cache + l1_data_cache) // 1024
                if total_l1_cache_kb > 0:
                    cache_sizes["l1"] = f"{total_l1_cache_kb} KB"
            else:
                raise TypeError("`psutil` return an unexpected type for L1 cache size.")

            # The cpuinfo library has an issue where it reports the L2 cache size as a
            # string with a unit of "MiB," even though the value provided is in MB.
            # While the numerical value is accurate in MB, the unit label "MiB" is
            # incorrect and misleading.
            l2_cache_raw = self._raw_cpu_info.get("l2_cache_size", None)
            if isinstance(l2_cache_raw, str) and "MiB" in l2_cache_raw:
                cache_sizes["l2"] = l2_cache_raw.replace("MiB", "MB")
            elif isinstance(l2_cache_raw, int):
                if l2_cache_raw > 0:
                    cache_sizes["l2"] = f"{l2_cache_raw // (1024 * 1024)} MB"
            else:
                raise TypeError("`psutil` return an unexpected type for L2 cache size.")

            l3_cache_raw = self._raw_cpu_info.get("l3_cache_size", None)
            if isinstance(l3_cache_raw, int):
                l3_cache_mb = l3_cache_raw // (1024 * 1024)
                cache_sizes["l3"] = f"{l3_cache_mb} MB"
            else:
                raise TypeError("`psutil` return an unexpected type for L3 cache size.")

        except TypeError as e:
            logger.exception(
                "An error ocurred when querying `psutil` for cache sizes. Error: {e}"
            )
            raise TypeError from e

        except Exception as e:
            logger.exception(
                "An unexpected error ocurred when querying `psutil` for cpu cache"
                "sizes. Error: {e}"
            )
            raise Exception from e

        return cache_sizes

    async def get_details(self) -> dict:
        """Creates a detailed dictionary of general information about the CPU.

        This method returns key details about the system's CPU, including:
        - Vendor (e.g., Intel, AMD)
        - Model (e.g., Intel Core i7-10700K)
        - Architecture (e.g., x86_64, ARM)
        - Core count (physical cores)
        - Logical processor count (threads)
        - CPU frequency (minimum, maximum and turbo)
        - Cache sizes (L1, L2, L3)

        Returns:
            dict: A dictionary containing the following keys:
                - 'vendor': The CPU vendor (e.g., Intel, AMD)
                - 'model': The full CPU model name
                - 'architecture': The CPU architecture (e.g., x86_64)
                - 'socket': The CPU socket type
                - 'cores': The number of physical cores
                - 'threads': The number of logical processors (threads)
                - 'min_frequency': The base CPU frequency in GHz
                - 'max_frequency': The maximum CPU frequency in GHz
                - 'turbo_frequency': The maximum Turbo Boost CPU frequency in GHz
                - 'cache_sizes': A dictionary with L1, L2, and L3 cache sizes in bytes

        Example:
            cpu_info = cpu_details.get_cpu_info()
            print(cpu_info['vendor'])  # Output: 'Intel'
            print(cpu_info['cores'])   # Output: 8

        Note:
            Some details, such as the model or vendor, may not be available on all
            systems. The method will try to fetch as much information as possible, but
            results may vary depending on the platform and the available system
            libraries.
        """
        cpu_info = {}
        try:
            raw_cpu_freq = psutil.cpu_freq()
            cpu_core_count = psutil.cpu_count(logical=False)
            cpu_thread_count = psutil.cpu_count(logical=True)
        except Exception:
            logger.exception(
                "An unexpected error ocurred when retrieving cpu details from the"
                "`psutil` module."
            )

        cpu_turbo_freq = await self._get_turbo_frequency_linux()
        cpu_cache_sizes = await self._get_cpu_cache_sizes()

        cpu_info["vendor"] = self._raw_cpu_info.get("vendor_id_raw", "Unknown")
        cpu_info["model"] = self._raw_cpu_info.get("brand_raw", "Unknown")
        cpu_info["architecture"] = self._raw_cpu_info.get("arch", "Unknown")
        cpu_info["socket"] = self._raw_cpu_info.get("hardware_raw", "Unknown")
        cpu_info["cores"] = cpu_core_count if cpu_core_count else "Unknown"
        cpu_info["threads"] = cpu_thread_count if cpu_thread_count else "Unknown"
        cpu_info["min_frequency"] = raw_cpu_freq.min if raw_cpu_freq.min else "Unknown"
        cpu_info["max_frequency"] = raw_cpu_freq.max if raw_cpu_freq.max else "Unknown"
        cpu_info["turbo_frequency"] = cpu_turbo_freq if cpu_turbo_freq else "Unknown"
        cpu_info["cache_sizes"] = cpu_cache_sizes

        return cpu_info
