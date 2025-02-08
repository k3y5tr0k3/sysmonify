"""utils.py.

This module contains utility classes that are used by multiple GPU tasks.

Classes:
    NvidiaSMI:
        An interface for the 'nvidia-smi' command-line utility.

    LSPCI:
        An interface for 'lspci' command-line utility.
"""

import csv
import logging

from sysmonify.core.utils import run_command_async


logger = logging.getLogger(__name__)


class NvidiaSMI:
    """A static class for asynchronously interfacing with the 'nvidia-smi' command-line utility.

    Methods:
        query_gpu(headers: list) -> list:
            Queries GPU information.
    """

    @staticmethod
    async def query_gpu(headers: list) -> list:
        """Asynchronously queries GPU information via 'nvidia-smi' command.

        Args:
            headers (list[str]):
                A list of column headers to query 'nvidia-smi' with. For a full list of
                available headers run `nvidia-smi --help-query-gpu` in the terminal.

        Returns:
            list[dict]:
                A list of dictionaries where the keys are the given headers.
        """
        gpu_info = []

        command = [
            "nvidia-smi",
            f"--query-gpu={','.join(headers)}",
            "--format=csv,nounits",
        ]

        try:
            output = await run_command_async(command=command)

            if output["exit_code"] != 0:
                raise Exception(output["stderr"])

            output_lines = output["stdout"].split("\n")
            output_lines = [line.strip("\n") for line in output_lines]

            reader = csv.DictReader(output_lines)
            gpu_info = [
                {key.strip(): value.strip() for key, value in row.items()}
                for row in reader
            ]

        except csv.Error as e:
            logger.exception(
                f"Error: Issue while parsing CSV output of nvidia-smi - {e}"
            )

        except Exception as e:
            logger.exception(f"Error occurred when running 'nvidia-smi': Error: {e}")

        return gpu_info


class LSPCI:
    """A static class for asynchronously interfacing with the 'lspci' command-line utility.

    Methods:
        get_gpu_vendors() -> set:
            Asynchronously retrieves a set of vendor names of all GPUs installed on a
            system.
    """

    @staticmethod
    async def get_gpu_vendors() -> set:
        """Asynchronously runs the 'lspci' command and filters output for GPU vendors.

        Returns:
            set[str]:
                A set containing all GPU vendor names of GPUs installed on the system.
        """
        gpu_vendors = set()

        try:
            result = await run_command_async(["lspci", "-nn"])

            if result["exit_code"] != 0:
                raise Exception(result["stderr"])

            lines = result["stdout"].splitlines()

            for line in lines:
                if "VGA" in line or "3D" in line:
                    if "NVIDIA" in line:
                        gpu_vendors.add("NVIDIA")
                    elif "AMD" in line:
                        gpu_vendors.add("AMD")
                    elif "Intel" in line:
                        gpu_vendors.add("Intel")

        except Exception as e:
            logger.exception(
                f"Unexpected error occurred when querying lspci for available GPUs: {e}"
            )

        return gpu_vendors
