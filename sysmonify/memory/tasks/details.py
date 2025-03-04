"""details.py.

A module containing classes for retrieving details about installed memory on the system.

Classes:
    MemoryDetails:
        A class for retrieving details of memory installed on a system such as vendors,
        models, sizes and more.
"""


class MemoryDetails:
    """Retrieves per-module memory details.

    TODO: It seems that the only way to retrieve details memory information is via BIOS
    or DMI table which requires sudo privileges. This class will therefore be
    implemented in a later release.
    """

    ...
