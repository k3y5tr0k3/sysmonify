"""monitors.py.

A module containing classes for retrieving real-time memory stats.

Classes:
    MemoryMonitor:
        A class for retrieving real-time memory and swap stats.
"""

import logging

from sysmonify.core.tasks import Monitor


logger = logging.getLogger(__name__)


class MemoryMonitor(Monitor):
    """A class for retrieving real-time memory and swap stats.

    Reads real-time memory metrics from /proc/meminfo and returns the metrics in a
    dictionary.

    Methods:
        _get_memory_info() -> dict:
            Reads and parses memory information from the /proc/meminfo file.

        get_metrics() -> dict:
            Retrieves real-time memory metrics and returns a dictionary.
    """

    def _get_memory_info(self) -> dict:
        """Reads and parses memory information from the /proc/meminfo file.

        This method attempts to open and read the contents of the `/proc/meminfo` file,
        which contains various memory statistics on Linux systems. The file is parsed
        line-by-line, splitting each line into a key-value pair, where the key is the
        memory metric name and the value is the corresponding memory value (e.g.,
        total memory, free memory). All parsed memory statistics are returned as a
        dictionary.

        If an error occurs while reading the file (e.g., file not found, I/O error),
        the exception is logged.

        Returns:
            dict:
                A dictionary where the keys are memory metric names (e.g., 'MemTotal',
                'MemFree') and the values are the corresponding memory values in
                kilobytes (e.g., 8192, 2048).

        Raises:
            FileNotFoundError:
                If the /proc/meminfo file is not found on the system.

            IOError:
                If there is an issue reading the /proc/meminfo file.

            Exception:
                For any other unexpected errors during file access.
        """
        mem_stats = {}

        try:
            with open("/proc/meminfo", "r") as file:
                for line in file:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().split()[0]
                        mem_stats[key] = int(value)

        except FileNotFoundError:
            logger.exception("/proc/meminfo file not found.")

        except IOError as e:
            logger.exception(f"IOError while opening /proc/meminfo: {e}")

        except Exception as e:
            logger.exception(f"Unexpected error while accessing /proc/meminfo: {e}")

        return mem_stats

    def get_metrics(self) -> dict:
        """Retrieves real-time memory and swap metrics from the system.

        This method gathers memory and swap statistics, such as total, used, and free
        memory, by reading from the system's memory information (e.g., `/proc/meminfo`
        on Linux). It calculates used memory as the total memory minus free memory,
        buffers, and cached memory, and similarly computes swap usage.

        If memory information cannot be retrieved, it returns a dictionary with all
        values set to 0.

        Returns:
            dict:
                A dictionary containing memory and swap metrics with the following
                structure:
                    {
                        "memory": {
                            "total": int,  # Total physical memory in kB
                            "used": int,   # Used memory in kB
                            "free": int,   # Free memory in kB
                        },
                        "swap": {
                            "total": int,  # Total swap memory in kB
                            "used": int,   # Used swap memory in kB
                            "free": int,   # Free swap memory in kB
                        }
                    }

        Example:
            {
                "memory": {"total": 8192, "used": 4096, "free": 4096},
                "swap": {"total": 2048, "used": 1024, "free": 1024}
            }
        """
        metrics = {
            "memory": {"total": 0, "used": 0, "free": 0},
            "swap": {"total": 0, "used": 0, "free": 0},
        }

        mem_info = self._get_memory_info()

        if mem_info:
            mem_total = mem_info.get("MemTotal", 0)
            mem_free = mem_info.get("MemFree", 0)
            buffers = mem_info.get("Buffers", 0)
            cached = mem_info.get("Cached", 0)
            mem_used = mem_total - (mem_free + buffers + cached)

            metrics["memory"]["total"] = mem_total
            metrics["memory"]["used"] = mem_used
            metrics["memory"]["free"] = mem_free

            swap_total = mem_info.get("SwapTotal", 0)
            swap_free = mem_info.get("SwapFree", 0)
            swap_used = swap_total - swap_free

            metrics["swap"]["total"] = swap_total
            metrics["swap"]["used"] = swap_used
            metrics["swap"]["free"] = swap_free

        return metrics
