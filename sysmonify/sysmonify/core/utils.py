"""utils.py.

A collection of utility functions.
"""

import pathlib
import asyncio
import logging

import aiofiles


logger = logging.getLogger(__name__)


async def read_file_async(filepath: pathlib.Path) -> str | None:
    """Reads a file asynchronously.

    Args:
        filepath (pathlib.Path): Path to the file.

    Returns:
        str | None: File contents, or None
    """
    file_lines = []

    try:
        async with aiofiles.open(filepath, "r") as f:
            file_lines = await f.readlines()

    except FileNotFoundError:
        logger.exception(f"Error: The file '{filepath}' was not found.")

    except PermissionError:
        logger.exception(
            f"Error: Permission denied when trying to access '{filepath}'."
        )

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")

    return file_lines


async def run_command_async(command: list):
    """Run an async subprocess command with error handling.

    Args:
        command (list): Command and arguments as a list. Example: ["ls", "-l"]

    Returns:
        dict: A dictionary with 'stdout', 'stderr', and 'exit_code'
    """
    try:
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        return {
            "exit_code": process.returncode,
            "stdout": stdout.decode().strip(),
            "stderr": stderr.decode().strip(),
        }

    except FileNotFoundError:
        logger.exception(f"Error: Command not found: {command[0]}")
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Command not found: {command[0]}",
        }

    except asyncio.TimeoutError:
        logger.exception(f"Error: Command timed out: {command}")
        return {"exit_code": -1, "stdout": "", "stderr": "Command timed out"}

    except Exception as e:
        logger.exception(f"Unexpected error running command {command}: {e}")
        return {"exit_code": -1, "stdout": "", "stderr": str(e)}
