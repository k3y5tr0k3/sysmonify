"""test_details.py.

This module contains unit tests for cpu.tasks.details
"""

import asyncio

from django.test import TestCase

from cpu.tasks.details import CPUDetails


class TestCPUDetails(TestCase):
    """Tests for `CPUDetails` class."""

    def setUp(self):
        """Initialize test class."""
        self.cpu_details = CPUDetails()

    def test_get_cpu_info_returns_dict_with_expected_keys(self) -> None:
        """Test that the `get_cpu_info()` method returns a valid dictionary with all the expected keys.

        Asserts:
            - The value returned from `get_cpu_info()` is of type `dict`
            - The following keys are present in the dictionary:
                - vendor
                - model
                - architecture
                - socket
                - cores
                - threads
                - min_frequency
                - max_frequency
                - turbo_frequency
                - cache_sizes
        """
        cpu_info = asyncio.run(self.cpu_details.get_details())

        assert isinstance(cpu_info, dict)
        assert "vendor" in cpu_info
        assert "model" in cpu_info
        assert "architecture" in cpu_info
        assert "socket" in cpu_info
        assert "cores" in cpu_info
        assert "threads" in cpu_info
        assert "min_frequency" in cpu_info
        assert "max_frequency" in cpu_info
        assert "cache_sizes" in cpu_info
