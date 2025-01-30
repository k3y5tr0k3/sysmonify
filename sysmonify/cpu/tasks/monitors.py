"""monitors.py.

This module contains classes and utilities for retrieving CPU data and real-time
system statistics. These classes provide a structured way to monitor and collect
system performance metrics, such as CPU utilization, frequency, and temperature.

Classes:
    - CPUFreqMonitor:
        A class for continuously monitoring real-time statistics, such as CPU usage
        percentage and load average.
    - CPUThermalMonitor:
        A class to fetch thermal data for the CPU, including sensor readings.

Usage:
    This module is intended to be used as part of the background task system for
    periodic monitoring or on-demand requests. It can be integrated with task
    queues like Celery for scheduled data collection or used standalone in scripts.

Examples:
    - Fetching CPU data:
        monitor = CPUData()
        cpu_details = monitor.get_cpu_info()

    - Fetching thermal zone temperatures:
        thermal = CPUThermalMonitor()
        cpu_temp = thermal.get_cpu_temperature()

Dependencies:
    - psutil:
        Used for retrieving CPU and system statistics.
    - py-cpuinfo:
        Detailed information about a CPU (Vendor, Model, etc).

Note:
    Ensure required permissions are available for accessing system-level data,
    especially for temperature sensors.
"""

import logging

import psutil

from sysmonify.core.tasks import Monitor


logger = logging.getLogger(__name__)


class CPUFreqMonitor(Monitor):
    """A class to monitor and retrieve the current CPU frequency for each core in the system.

    This class provides functionality to query the system for the current CPU frequency
    for each core. It is useful for monitoring CPU performance, identifying high usage,
    or performance issues.

    Attributes:
        None

    Methods:
        get_metrics() -> dict:
            Retrieves the current CPU frequencies for all cores on the system.
            Returns a dictionary where the keys are the CPU core numbers and
            the values are the current frequency in Hz.
    """

    async def get_metrics(self) -> dict:
        """Retrieve the current CPU frequencies for all cores.

        This method iterates through the per-core CPU frequency data and returns
        a dictionary where the keys represent each core (e.g., "Core 0") and the
        values are the current CPU frequencies in MHz.

        Returns:
            dict:
                A dictionary containing the current frequency of each core
                (e.g., {"Core 0": 2600.00, "Core 1": 2600.50, ...}).

        Raises:
            AttributeError:
                If `self.cpu_freq` is not set or does not contain valid frequency data.
            TypeError:
                If the elements in `self.cpu_freq` are not iterable or lack the
                `current` attribute.
        """
        current_freq = {}

        try:
            cpu_freq = psutil.cpu_freq(percpu=True)

            for core, freq in enumerate(cpu_freq):
                if not hasattr(freq, "current"):
                    raise TypeError(
                        f"Core `{core}` frequency object does not have a 'current'"
                        "attribute."
                    )
                current_freq[f"Core {core}"] = freq.current

        except AttributeError as e:
            raise AttributeError(
                "The 'cpu_freq' attribute is missing or invalid."
            ) from e

        except RuntimeError as e:
            raise RuntimeError(f"Failed to retrieve CPU frequencies: {str(e)}") from e

        except TypeError as e:
            raise TypeError(f"Invalid structure in 'cpu_freq': {str(e)}") from e

        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while retrieving CPU frequencies: {str(e)}"
            ) from e

        return current_freq


class CPUThermalMonitor(Monitor):
    """A class to monitor and retrieve the current CPU package temperature.

    This class provides functionality to query the system for the current CPU package
    temperature. It is useful for monitoring thermal performance, detecting overheating
    issues, and ensuring efficient cooling.

    Attributes:
        None

    Methods:
        get_metrics() -> dict:
            Retrieves the current CPU package temperature. Returns a dictionary where
            the keys are the CPU temperature sensor labels and the values are the
            current temperature in degrees celsius. Current only support CPU package
            temp.

    """

    async def get_metrics(self) -> dict:
        """Retrieve the current CPU temperature.

        This method retrieves CPU package temperature from the system and returns an
        integer in degrees celsius.

        Returns:
            dict:
                A dictionary containing the current frequency of each core
                (e.g., {"Package": "66.2"}).

        Raises:
            AttributeError:
                If the system does not support temperature readings
        """
        temps = {"package": "Unknown"}

        try:
            sensor_temps = psutil.sensors_temperatures()
            if sensor_temps and "coretemp" in sensor_temps:
                for sensor in sensor_temps.get("coretemp", []):
                    if "Package id 0" in sensor.label:
                        temps["package"] = str(sensor.current)
                        break

        except AttributeError:
            raise AttributeError("Temperature readings not supported on this system.")

        except KeyError as e:
            raise KeyError(f"Unexpected key error: {str(e)}") from e

        except TypeError as e:
            raise TypeError(
                f"Type error while processing temperature data: {str(e)}"
            ) from e

        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}") from e

        return temps
