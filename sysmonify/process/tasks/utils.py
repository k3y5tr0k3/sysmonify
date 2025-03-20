"""utils.py.

A collection of utility functions and classes that are commonly used by process app
tasks.

"""

import re
import logging

from sysmonify.core.utils import run_command_async


logger = logging.getLogger(__name__)


class Top:
    """A static class for asynchronously interacting with the `top` linux command line utility."""

    @staticmethod
    async def get_processes() -> dict:
        """Retrieve a dictionary of currently running processes asynchronously.

        This method executes the `top` command in batch mode (`-b -n 1`) to fetch a snapshot
        of running processes. It then parses the output to extract relevant process details.

        Returns:
            dict: A dictionary where keys are process IDs (PIDs) and values are dictionaries
            containing process details:
                - "USER" (str): Owner of the process.
                - "PR" (str): Process priority.
                - "NI" (str): Nice value.
                - "VIRT" (str): Virtual memory size.
                - "RES" (str): Resident memory size.
                - "SHR" (str): Shared memory size.
                - "S" (str): Process state.
                - "CPU%" (float): CPU usage percentage.
                - "MEM%" (float): Memory usage percentage.
                - "TIME+" (str): Cumulative CPU time.
                - "COMMAND" (str): Full command used to launch the process.

        Raises:
            Exception: If the `top` command fails to execute (non-zero exit code),
            an exception is raised with the error message from stderr."
        """
        output = await run_command_async(command=["top", "-b", "-n", "1"])

        if output["exit_code"] != 0:
            raise Exception(output["stderr"])

        # ignore first 7 lines (headers)
        lines = output["stdout"].split("\n")[7:]

        processes = {}
        for line in lines:
            parts = re.split(r"\s+", line.strip())
            if len(parts) < 12:
                continue

            try:
                pid = int(parts[0])
                process_info = {
                    "USER": parts[1],
                    "PR": parts[2],
                    "NI": parts[3],
                    "VIRT": parts[4],
                    "RES": parts[5],
                    "SHR": parts[6],
                    "S": parts[7],
                    "CPU%": float(parts[8]),
                    "MEM%": float(parts[9]),
                    "TIME+": parts[10],
                    "COMMAND": " ".join(parts[11:]),
                }
                processes[pid] = process_info

            except ValueError:
                continue

        return processes
