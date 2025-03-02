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
        get_metrics() -> dict:
            Retrieves real-time memory metrics and returns a dictionary.
    """

    def get_metrics(self) -> dict:
        """Retrieves real-time memory metrics and returns a dictionary.

        Returns:
            dict:
        """
        metrics = {
            "memory": {"total": "0 KB", "free": "0 KB"},
            "swap": {"total": "0 KB", "free": "0 KB"},
        }

        try:
            with open("/proc/meminfo", "r") as file:
                for line in file:
                    try:
                        if line.startswith("MemTotal"):
                            total_mem = line.split(":")[1].strip()
                            metrics["memory"]["total"] = total_mem

                        if line.startswith("MemFree"):
                            free_mem = line.split(":")[1].strip()
                            metrics["memory"]["free"] = free_mem

                        if line.startswith("SwapTotal"):
                            total_swap = line.split(":")[1].strip()
                            metrics["swap"]["total"] = total_swap

                        if line.startswith("SwapFree"):
                            free_swap = line.split(":")[1].strip()
                            metrics["swap"]["free"] = free_swap

                    except ValueError as e:
                        logger.error(
                            f"ValueError while parsing line: {line}. Error: {e}"
                        )

                    except IndexError as e:
                        logger.error(
                            f"IndexError while parsing line: {line}. Error: {e}"
                        )

                    except Exception as e:
                        logger.error(
                            f"Unexpected error while parsing line: {line}. Error: {e}"
                        )

        except FileNotFoundError:
            logger.error("/proc/meminfo file not found.")

        except IOError as e:
            logger.error(f"IOError while opening /proc/meminfo: {e}")

        except Exception as e:
            logger.error(f"Unexpected error while accessing /proc/meminfo: {e}")

        return metrics
