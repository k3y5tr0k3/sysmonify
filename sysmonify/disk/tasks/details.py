"""details.py.

This module provides functionality to retrieve and display detailed information about
the disks and their partitions on a Linux-based system. It leverages and tools like
`lsblk`, and system files to gather disk-related data.

Classes:
    DiskDetails:
        A class for retrieving details about disks and partitions on the system.
"""

import json
import logging
import pathlib
import subprocess

from sysmonify.core.tasks import Details


logger = logging.getLogger(__name__)


class DiskDetails(Details):
    """A class to retrieving detailed information about the disks and their partitions.

    The class interacts with system files and tools such as `/sys`, `lsblk`, and others
    to gather essential disk and partition-related data, including sizes, filesystem
    types, mount points, and additional metadata.

    Attributes:
        LSBLK_HEADERS (list):
            A list of column headers for `lsblk` subprocess to return.

    Methods:
        get_details():
            Retrieve and return a dictionary containing detail information about disks
            and their partitions.
    """

    def __init__(self) -> None:
        """Default initializer."""
        self._LSBLK_HEADERS = [
            "NAME",
            "LABEL",
            "TYPE",
            "SERIAL",
            "SIZE",
            "MOUNTPOINT",
            "VENDOR",
            "MODEL",
            "VENDOR",
            "PATH",
            "PARTN",
            "PARTTYPENAME",
            "FSTYPE",
            "FSVER",
            "TRAN",
            "PTTYPE",
            "UUID",
            "ROTA",
        ]

    def _get_disk_space_utilization(self) -> dict: ...

    def _get_raw_block_devices(self) -> dict:
        """Executes the 'lsblk' command and returns block device information as a Python dictionary.

        Returns:
            dict: Parsed JSON output from 'lsblk' containing block device details.
            None: If an error occurs during execution.

        Errors:
            - Captures and logs any errors from the 'lsblk' command.
            - Returns None if 'lsblk' is not found or fails to execute.
        """
        disk_details = {}

        try:
            result = subprocess.run(
                [
                    "lsblk",
                    "-J",
                    "-o",
                    ",".join(self._LSBLK_HEADERS),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            disk_details = json.loads(result.stdout)

        except FileNotFoundError:
            logger.exception(
                "Error: 'lsblk' command not found. Ensure it is installed and"
                "accessible."
            )

        except subprocess.CalledProcessError as e:
            logger.exception(f"Error executing 'lsblk': {e}")

        except json.JSONDecodeError:
            logger.exception("Error: Failed to parse 'lsblk' JSON output.")

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")

        return disk_details.get("blockdevices")

    def _is_physical_disk(self, block_device_name: str) -> bool:
        """Check if the given block device is a physical disk.

        Constructs an expected symbolic link for a block device then uses linux built-in
        `readlink` command to return the actual location of the device. If the device
        path contains a directory named "virtual" (or if it does not exist) we assume it
        is a virtual disk, otherwise we can assume it is a physical device.

        Args:
            block_device_name (str):
                The name given to the block device by the kernel. e.g. `sda`, `sdb`.

        Returns:
            bool:
                True if block device is a physical disk, otherwise False.

        Raises:
            FileNotFoundError:
                If the symbolic link for the block device does not exist.

            PermissionError:
                If access to the symbolic link is denied due to insufficient
                permissions.

            OSError:
                If an OS-related error occurs while resolving the symbolic link.

            Exception:
                If an unexpected error occurs during execution.
        """
        symlink = f"/sys/block/{block_device_name}"
        is_physical = True

        try:
            resolved_path = pathlib.Path(symlink).resolve(strict=True)

            if "virtual" in str(resolved_path):
                is_physical = False

        except FileNotFoundError:
            logger.exception(
                f"Error: The block device '{block_device_name}' does not exist with "
                f"symlink {symlink}."
            )
            is_physical = False

        except PermissionError:
            logger.exception(f"Error: Permission denied when accessing '{symlink}'.")
            is_physical = False

        except OSError as e:
            logger.exception(f"Error: OS-related issue when resolving '{symlink}': {e}")
            is_physical = False

        except Exception:
            logger.exception(
                "An unexpected exception was raised when attempting to determine if "
                f"device {block_device_name} is a physical disk."
            )
            is_physical = False

        return is_physical

    def _get_physical_disks_from_raw_block_devices(
        self, raw_block_devices: dict
    ) -> list:
        """Filters and returns a list of physical disk devices from a given list of raw block devices.

        This method iterates through a list of block devices, checks if each device is
        of type "disk," and then verifies whether it is a physical disk using
        `_is_physical_disk()`. Only physical disks are included in the returned list.

        Args:`
            `raw_block_devices` (list):
                A list of dictionaries representing block devices, where each
                dictionary contains at least a "type" and "name" key.

        Returns:
            `list`:
                A list of dictionaries representing physical disks.
        """
        physical_disks = []

        for device in raw_block_devices:
            if device.get("type", "") == "disk":
                device_name = device.get("name")
                if self._is_physical_disk(block_device_name=device_name):
                    if device.get("vendor", None) is None:
                        device["vendor"] = "Unknown"
                    physical_disks.append(device)

        return physical_disks

    async def get_details(self) -> dict:
        """Retrieve and return a dictionary containing detail information about disks and their partitions.

        Gathers disk and partition details for all disks, consolidates it and returns a
        dictionary containing all relevant information such as device name, vendor,
        model, size, filesystem type and more.

        Returns:
            `dict`:
                A dictionary containing all relevant information related to disks and
                their partitions.
        """
        disks = {}

        raw_block_devices = self._get_raw_block_devices()
        disks = self._get_physical_disks_from_raw_block_devices(
            raw_block_devices=raw_block_devices
        )

        return disks
