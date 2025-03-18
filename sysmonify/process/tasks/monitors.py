"""monitors.py.

A collection of real-time monitors for processes running on a system.

Classes:
    ProcessMonitor:
        A class for real-time monitoring of processes running on a linux system.
"""

import logging

from sysmonify.core.tasks import Monitor
from process.tasks.utils import Top

logger = logging.getLogger(__name__)


class ProcessMonitor(Monitor):
    """A class for real-time monitoring of processes running on a linux system.

    Methods:
        get_metrics() -> dict:
            Retrieves a dictionary of currently running processes and process data.
    """

    def get_process_command(self, pid: int) -> str | None:
        r"""Retrieves the full command string for a given process ID (PID).

        This function reads the `/proc/{pid}/cmdline` file to get the command
        that started the process, replacing null characters (`\0`) with spaces.

        Args:
            pid (int): The process ID whose command string needs to be retrieved.

        Returns:
            str | None: The full command string if successfully retrieved,
            otherwise `None`.

        Raises:
            Exception: Logs an error if reading the command fails.
        """
        command = None
        try:
            with open(f"/proc/{pid}/cmdline", "r") as f:
                command = f.read().strip().replace("\0", " ")

        except Exception as e:
            logger.debug(
                "Error occurred while retrieving the full command string for pid "
                f"`{pid}`. {e}"
            )

        return command

    async def get_metrics(self) -> dict:
        """Collect system metrics for running processes."""
        metrics = {}

        try:
            processes = await Top.get_processes()

            if processes:
                for pid, process_info in processes.items():
                    command = self.get_process_command(pid=pid)

                    metrics[pid] = {
                        "command": command
                        if command
                        else process_info.get("COMMAND+", "Unknown"),
                        "user": process_info.get("USER", "Unknown"),
                        "cpu": process_info.get("CPU%", 0),
                        "memory": process_info.get("MEM%", 0),
                        "up_time": process_info.get("TIME+", "00:00:00"),
                    }

        except Exception as e:
            logging.exception(f"Error in get_metrics: {e}")

        return metrics
