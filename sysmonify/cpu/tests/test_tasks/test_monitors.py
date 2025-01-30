"""test_monitors.py.

This module contains unit tests for cpu.tasks.monitors
"""

import asyncio
import unittest
import collections

from django.test import TestCase

from cpu.tasks.monitors import CPUFreqMonitor, CPUThermalMonitor


class TestCPUFreqMonitor(TestCase):
    """Test class for CPUFreqMonitor."""

    def setUp(self):
        """Setup test class."""
        self.instance = CPUFreqMonitor()

    @unittest.mock.patch("psutil.cpu_freq")
    def test_get_metrics_valid_data(self, mock_cpu_freq):
        """Test with valid per-core frequency data.

        Asserts:
            Given specific outputs from `psutil.cpu_freq` the output of `get_metrics`
            has the expected format, types and values.
        """
        mock_cpu_freq.return_value = [
            unittest.mock.MagicMock(current=2600.00),
            unittest.mock.MagicMock(current=2601.50),
        ]
        expected_output = {"Core 0": 2600.00, "Core 1": 2601.50}

        result = asyncio.run(self.instance.get_metrics())

        self.assertEqual(result, expected_output)

    @unittest.mock.patch("psutil.cpu_freq")
    def test_get_metrics_missing_current_attribute(self, mock_cpu_freq):
        """Test with frequency data missing the 'current' attribute.

        Asserts:
            TypeError is raised when `psutil.cpu_freq` does not contain a 'current'
            attribute.
        """
        mock_cpu_freq.return_value = [
            unittest.mock.MagicMock(),
            unittest.mock.MagicMock(),
        ]
        del mock_cpu_freq.return_value[0].current

        with self.assertRaises(TypeError) as context:
            asyncio.run(self.instance.get_metrics())
        self.assertIn("Invalid structure in 'cpu_freq'", str(context.exception))

    @unittest.mock.patch("psutil.cpu_freq")
    def test_get_metrics_cpu_freq_fails(self, mock_cpu_freq):
        """Test when psutil.cpu_freq raises a Exception when psutil fails.

        Asserts:
            Exception is raised when `psutil.cpu_freq` raises an exception.
        """
        mock_cpu_freq.side_effect = Exception("Failed to retrieve frequencies")

        with self.assertRaises(Exception) as context:
            asyncio.run(self.instance.get_metrics())
        self.assertIn("Failed to retrieve frequencies", str(context.exception))

    @unittest.mock.patch("psutil.cpu_freq")
    def test_get_metrics_invalid_structure(self, mock_cpu_freq):
        """Test when psutil.cpu_freq returns an invalid structure.

        Asserts:
            TypeError is raised when `psutil.cpu_freq` returns an invalid structure.
        """
        mock_cpu_freq.return_value = ["invalid_data"]

        with self.assertRaises(TypeError) as context:
            asyncio.run(self.instance.get_metrics())
        self.assertIn("Invalid structure in 'cpu_freq'", str(context.exception))


class TestCPUThermalMonitor(TestCase):
    """Test cases for CPUThermalMonitor class."""

    def setUp(self):
        """Set up any state required for the tests."""
        self.monitor = CPUThermalMonitor()
        self.shwtemp = collections.namedtuple("shwtemp", ["label", "current"])

    @unittest.mock.patch("psutil.sensors_temperatures")
    def test_get_metrics_success(self, mock_sensors_temperatures):
        """Test successful retrieval of CPU package temperature.

        Asserts:
            Given specific outputs from `psutil.cpu_freq` the output of `get_metrics`
            has the expected format, types and values.
        """
        mock_sensors_temperatures.return_value = {
            "coretemp": [
                self.shwtemp(label="Package id 0", current=55.0),
                self.shwtemp(label="Core 0", current=40.0),
                self.shwtemp(label="Core 1", current=42.0),
            ]
        }

        result = asyncio.run(self.monitor.get_metrics())

        self.assertEqual(result, {"package": "55.0"})

    @unittest.mock.patch("psutil.sensors_temperatures")
    def test_get_metrics_no_package(self, mock_sensors_temperatures):
        """Test when no 'Package id 0' sensor is available.

        Asserts:
            If `psutil.sensors_temperatures.coretemp` does not contain `Package id 0`
            `get_metrics`returns the expected format, types and values.
        """
        mock_sensors_temperatures.return_value = {
            "coretemp": [
                self.shwtemp(label="Core 0", current=40.0),
                self.shwtemp(label="Core 1", current=42.0),
            ]
        }

        result = asyncio.run(self.monitor.get_metrics())

        self.assertEqual(result, {"package": "Unknown"})

    @unittest.mock.patch("psutil.sensors_temperatures")
    def test_get_metrics_no_sensors(self, mock_sensors_temperatures):
        """Test when no temperature sensors are found.

        Asserts:
            If `psutil` cannot access temperature sensors  `get_metrics`returns the
            expected format, types and values.
        """
        mock_sensors_temperatures.return_value = {}

        result = asyncio.run(self.monitor.get_metrics())

        self.assertEqual(result, {"package": "Unknown"})

    @unittest.mock.patch("psutil.sensors_temperatures")
    def test_get_metrics_attribute_error(self, mock_sensors_temperatures):
        """Test handling AttributeError when sensors are not supported.

        Asserts:
            If Attribute error is raise, it is handled correctly.
        """
        mock_sensors_temperatures.side_effect = AttributeError(
            "Temperature readings not supported on this system."
        )

        with self.assertRaises(AttributeError):
            asyncio.run(self.monitor.get_metrics())

    @unittest.mock.patch("psutil.sensors_temperatures")
    def test_get_metrics_key_error(self, mock_sensors_temperatures):
        """Test handling KeyError if an unexpected key is encountered.

        Asserts:
            If a KeyError is raised it is handled correctly.
        """
        mock_sensors_temperatures.side_effect = KeyError("Unexpected key error")

        with self.assertRaises(KeyError):
            asyncio.run(self.monitor.get_metrics())

    @unittest.mock.patch("psutil.sensors_temperatures")
    def test_get_metrics_type_error(self, mock_sensors_temperatures):
        """Test handling TypeError if there's a problem with data types.

        Asserts:
            If a TypeError is raised it is handled correctly.
        """
        mock_sensors_temperatures.side_effect = TypeError(
            "Type error while processing temperature data"
        )

        with self.assertRaises(TypeError):
            asyncio.run(self.monitor.get_metrics())

    @unittest.mock.patch("psutil.sensors_temperatures")
    def test_get_metrics_generic_exception(self, mock_sensors_temperatures):
        """Test handling any other unexpected exception.

        Asserts:
            If a generic Exception is raised it is handled correctly.
        """
        mock_sensors_temperatures.side_effect = Exception(
            "An unexpected error occurred"
        )

        with self.assertRaises(Exception):
            asyncio.run(self.monitor.get_metrics())
