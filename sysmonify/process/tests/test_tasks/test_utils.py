"""test_utils.py.

Unit tests for task utilities for the process app.
"""

import unittest
from unittest.mock import patch
from process.tasks.utils import Top


class TestTop(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the Top class."""

    @patch("process.tasks.utils.run_command_async")
    async def test_get_processes_success(self, mock_run_command_async):
        """Test that get_processes correctly parses top command output."""
        mock_top_output = """\
top - 10:00:00 up 1 day,  2:30,  1 user,  load average: 0.50, 0.40, 0.30
Tasks: 300 total,   1 running, 299 sleeping,   0 stopped,   0 zombie
%Cpu(s):  2.0 us,  1.0 sy,  0.0 ni, 97.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem :  8000000 total,  2000000 free,  3000000 used,  3000000 buff/cache
KiB Swap:  2000000 total,  2000000 free,        0 used.  5000000 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 1234 root      20   0  400000  20000   5000 S   5.0  1.0   00:02.34 python3
 5678 user1     20   0  500000  30000   6000 R   2.5  1.5   00:01.12 nginx
"""
        mock_run_command_async.return_value = {
            "stdout": mock_top_output,
            "stderr": "",
            "exit_code": 0,
        }

        # Call the method
        processes = await Top.get_processes()

        # Expected result
        expected_output = {
            1234: {
                "USER": "root",
                "PR": "20",
                "NI": "0",
                "VIRT": "400000",
                "RES": "20000",
                "SHR": "5000",
                "S": "S",
                "CPU%": 5.0,
                "MEM%": 1.0,
                "TIME+": "00:02.34",
                "COMMAND": "python3",
            },
            5678: {
                "USER": "user1",
                "PR": "20",
                "NI": "0",
                "VIRT": "500000",
                "RES": "30000",
                "SHR": "6000",
                "S": "R",
                "CPU%": 2.5,
                "MEM%": 1.5,
                "TIME+": "00:01.12",
                "COMMAND": "nginx",
            },
        }

        # Assertions
        self.assertEqual(processes, expected_output)

    @patch("process.tasks.utils.run_command_async")
    async def test_get_processes_failure(self, mock_run_command_async):
        """Test that get_processes raises an exception if the command fails."""
        mock_run_command_async.return_value = {
            "stdout": "",
            "stderr": "Error: top command failed",
            "exit_code": 1,
        }

        with self.assertRaises(Exception) as context:
            await Top.get_processes()

        self.assertEqual(str(context.exception), "Error: top command failed")
