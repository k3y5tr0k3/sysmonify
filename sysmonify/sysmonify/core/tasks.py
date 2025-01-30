"""monitors.py.

A module with a abstract base monitor that all other real-time hardware monitors
inherit from.

Classes:
    `Monitor`:
        An abstract base monitor that all other real-time hardware monitors inherit
        from.
"""

import abc


class Details(abc.ABC):
    """An abstract base monitor that all other hardware details retrievers inherit from.

    Methods:
        - `get_details()`:
            Retrieves details about a hardware resource.
    """

    @abc.abstractmethod
    def get_details(self) -> dict:
        """Retrieves details about hardware resource."""
        ...


class Monitor(abc.ABC):
    """An abstract base monitor that all other real-time hardware monitors inherit from.

    Methods:
        - `get_metrics()`:
            Retrieves current metrics for a hardware resource.
    """

    @abc.abstractmethod
    def get_metrics(self) -> dict:
        """Retrieves current metrics for a hardware resource."""
        ...
