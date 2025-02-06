"""monitors.py.

This module contains classes and utilities for retrieving real-time disk read/write
stats.

Classes:
    - DiskIOMonitor:
        A class for retrieving real-time read/write stats for all physical disks.

Examples:
    - Fetching current read/write speed:
        monitor = DiskIOMonitor()
        io = monitor.get_metrics()
"""

import logging
import datetime
import time

from sysmonify.core.tasks import Monitor


logger = logging.getLogger(__name__)


class DiskIOMonitor(Monitor):
    """Monitors real-time read/write speed for all physical disks using `/proc/diskstats`.

    This class reads disk statistics from `/proc/diskstats` at regular intervals to
    calculate the read and write speed in MB/s for each physical disk.

    Methods:
        `_get_disk_sectors()` -> dict:
            Read disk stats for a devices from /proc/diskstats.

        `_sectors_to_megabytes(sectors: int)` -> int:
            Converts disk sectors to megabytes.

        `get_metrics()` -> dict:
            Measures read and write speed for all physical disks..

    Example:
        monitor = DiskIOMonitor()
        metrics = monitor.get_metrics(interval=1)
        print(metrics)

        # Output:
        # {
        #   'sda': {
        #       'read_speed': 10.5,
        #       'write_speed': 5.2
        #   },
        #   'nvme0n1': {
        #       'read_speed': 20.3,
        #       'write_speed': 15.8
        #   }
        # }
    """

    def __init__(self, disks: list, smoothing_factor: float = 0.4) -> None:
        """Default initializer.

        Retrieves initial read and written sector values.

        Args:
            disks (list[str]):
                A list of disk names to monitor.

            smoothing_factor (float):
                Used for calculating exponential moving average speeds.

        """
        self._disks = disks
        self._smoothing_factor = smoothing_factor
        self._ema_speeds = {}
        self._previous_disks_sectors = self._get_current_disks_sectors()
        self._previous_timestamp = datetime.datetime.now()

    @property
    def disks(self):
        """Gets the value disks property."""
        return self._disks

    @disks.setter
    def disks(self, disks: list):
        """Sets the value of disks property.

        Args:
            disks (list):
                A list of disk names.
        """
        if disks != self._disks:
            self._disks = disks

    def _get_current_disks_sectors(self) -> dict:
        """Read disk stats for a devices from /proc/diskstats.

        Returns:
            dict:
                A dictionary where keys are device names (e.g., 'sda', 'nvme0n1') and
                values are dictionaries containing:
                    - 'read' (int): Current sectors read according to /proc/diskstats.
                    - 'written' (int): Current sectors written according to
                      /proc/diskstats.

        """
        disks_sectors = {}

        try:
            with open("/proc/diskstats", "r") as f:
                for line in f:
                    parts = line.split()
                    if parts[2] in self._disks:
                        try:
                            read_sectors = int(parts[5])
                            written_sectors = int(parts[9])

                            disks_sectors[parts[2]] = {
                                "read": read_sectors,
                                "written": written_sectors,
                            }
                        except ValueError as e:
                            logger.warning(
                                f"Failed to convert disk stats for {parts[2]}: {e}"
                            )

        except FileNotFoundError:
            logger.error(
                "/proc/diskstats file not found. Ensure the system supports this file."
            )
        except PermissionError:
            logger.error("Permission denied when trying to access /proc/diskstats.")
        except Exception as e:
            logger.error(f"Unexpected error while reading /proc/diskstats: {e}")

        return disks_sectors

    def _sectors_to_megabytes(self, sectors: int) -> int:
        """Converts disk sectors to megabytes.

        The kernel store disk read/write stats in sectors (512 bytes), this method
        converts a sectors value to the equivalent value in MB.

        Args:
            sectors (int):
                An arbitrary number of sectors each representing 512 bytes.

        Returns:
            int:
                An integer representing the MB equivalent of the given sectors.
        """
        mb = (sectors * 512) / (1024 * 1024)
        return mb

    def get_metrics(self):
        """Measures real-time read and write speed for all physical disks.

        Compares current sectors read and written for each disk and calculates the
        average read and write speeds (MB/s) since the previous measurement. Calculates
        the exponential moving average in order to smooth out read/write spikes caused
        by batch reads and writes.

        Returns:
            dict:
                A dictionary where keys are disk names (e.g., 'sda', 'nvme0n1') and
                values are dictionaries containing:
                    - 'read_speed' (float): Read speed in MB/s.
                    - 'write_speed' (float): Write speed in MB/s.
        """
        current_disks_speeds = {}
        current_disks_sectors = self._get_current_disks_sectors()
        current_timestamp = datetime.datetime.now()
        time_delta = current_timestamp - self._previous_timestamp
        time_delta_seconds = time_delta.total_seconds()

        for disk_name in self._disks:
            if disk_name not in self._previous_disks_sectors:
                continue

            current_disk_sectors = current_disks_sectors.get(disk_name, {})
            current_sectors_read = current_disk_sectors.get("read", 0)
            current_sectors_written = current_disk_sectors.get("written", 0)

            previous_disk_sectors = self._previous_disks_sectors[disk_name]
            read_sectors_delta = current_sectors_read - previous_disk_sectors.get(
                "read", 0
            )
            written_sectors_delta = current_sectors_written - previous_disk_sectors.get(
                "written", 0
            )

            read_delta_mb = self._sectors_to_megabytes(sectors=read_sectors_delta)
            written_delta_mb = self._sectors_to_megabytes(sectors=written_sectors_delta)

            read_mbps = (
                read_delta_mb / time_delta_seconds if read_delta_mb != 0 else 0.0
            )
            written_mbps = (
                written_delta_mb / time_delta_seconds if written_delta_mb != 0 else 0.0
            )

            if disk_name not in self._ema_speeds:
                self._ema_speeds[disk_name] = {
                    "read_speed": read_mbps,
                    "write_speed": written_mbps,
                }

            self._ema_speeds[disk_name]["read_speed"] = (
                self._smoothing_factor * read_mbps
                + (1 - self._smoothing_factor)
                * self._ema_speeds[disk_name]["read_speed"]
            )
            self._ema_speeds[disk_name]["write_speed"] = (
                self._smoothing_factor * written_mbps
                + (1 - self._smoothing_factor)
                * self._ema_speeds[disk_name]["write_speed"]
            )

            current_disks_speeds[disk_name] = {
                "read_speed": self._ema_speeds[disk_name]["read_speed"],
                "write_speed": self._ema_speeds[disk_name]["write_speed"],
            }

        self._previous_disks_sectors = current_disks_sectors
        self._previous_timestamp = current_timestamp

        return current_disks_speeds


if __name__ == "__main__":
    disks = ["nvme0n1"]
    monitor = DiskIOMonitor(disks=disks)
    while True:
        print(monitor.get_metrics())
        time.sleep(1)
