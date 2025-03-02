"""monitors.py.

A module for monitoring real-time network stats such as transfer-rates, packet stats
and more.

Classes:
    NetworkStatsMonitor:
        A class for retrieving real-time network statistics such as transmission speed
        and dropped packets.

    NetworkConnectionsMonitor:
        A class for retrieving real-time network connections and their related data,
        such as local address, foreign address
"""

import os
import pathlib
import socket
import struct
import hashlib
import logging
import datetime

from sysmonify.core.tasks import Monitor
from network.tasks.utils import get_physical_network_interfaces, IP


logger = logging.getLogger(__name__)


class NetworkStatsMonitor(Monitor):
    """A class for retrieving real-time network statistics for all network interfaces on the system.

    Methods:
        get_metrics() -> dict:
            Retrieve a dictionary of real-time network statistics for all network
            interfaces. Returns the Mbps values of RX and TX, and the number of packets
            dropped since the previous call.
    """

    def __init__(self):
        """Initializes the instance with default network statistics.

        This constructor sets up the object by initializing:
        - `_previous_network_stats`: A dictionary to store previous network statistics.
        - `_previous_timestamp`: A timestamp marking the last recorded network stats update.
        """
        self._previous_network_stats = {}
        self._previous_timestamp = datetime.datetime.now()

    async def get_metrics(self):
        """Retrieve network metrics and return a metrics dictionary.

        Gathers real-time metrics for all physical network interfaces. These metrics
        include:
            - RX mbps
            - TX mbps
            - Dropped packets

        Returns:
            dict:
                {
                    "rx_mbps": 0.123,
                    "tx_mbps": 0.00023,
                    "rx_dropped": 2,
                    "tx_dropped": 0
                }
        """
        metrics = {}
        interfaces = get_physical_network_interfaces()
        current_network_stats = {}
        current_timestamp = datetime.datetime.now()

        for interface in interfaces:
            try:
                current_network_stats[interface] = await IP.get_interface_stats(
                    interface_name=interface
                )

                if self._previous_network_stats.get(interface, None):
                    rx_bytes_delta = (
                        current_network_stats[interface]["rx"]["bytes"]
                        - self._previous_network_stats[interface]["rx"]["bytes"]
                    )
                    tx_bytes_delta = (
                        current_network_stats[interface]["tx"]["bytes"]
                        - self._previous_network_stats[interface]["tx"]["bytes"]
                    )
                    rx_dropped_delta = (
                        current_network_stats[interface]["rx"]["dropped"]
                        - self._previous_network_stats[interface]["rx"]["dropped"]
                    )
                    tx_dropped_delta = (
                        current_network_stats[interface]["tx"]["dropped"]
                        - self._previous_network_stats[interface]["tx"]["dropped"]
                    )

                    seconds = (
                        current_timestamp - self._previous_timestamp
                    ).total_seconds()

                    rx_mbps = (
                        rx_bytes_delta / 1024 / 1024 / seconds
                        if rx_bytes_delta > 0
                        else 0
                    )
                    tx_mbps = (
                        tx_bytes_delta / 1024 / 1024 / seconds
                        if tx_bytes_delta > 0
                        else 0
                    )

                    metrics[interface] = {
                        "rx_mbps": rx_mbps,
                        "tx_mbps": tx_mbps,
                        "rx_dropped": rx_dropped_delta,
                        "tx_dropped": tx_dropped_delta,
                    }

            except Exception as e:
                logger.exception(
                    "An error occurred while retrieving metric for network "
                    f"interface `{interface}`. {e}"
                )

        self._previous_timestamp = current_timestamp
        self._previous_network_stats = current_network_stats

        return metrics


class NetworkConnectionsMonitor(Monitor):
    """Monitors active network connections by parsing Linux `/proc/net` files.

    This class retrieves real-time network connection details, maps them to running
    processes, and provides insights into connection states, data transfer, and
    associated processes.

    Attributes:
        _PROC_FILES (list[tuple[pathlib.Path, str, int]]):
            A list of tuples containing file paths to `/proc/net` entries along with
            protocol and address family information (e.g., `tcp`, `udp`, `AF_INET`).

        _TCP_STATES (dict[str, str]):
            A mapping of hexadecimal TCP state codes (as found in `/proc/net/tcp`)
            to their human-readable state names (e.g., `"01"` → `"ESTABLISHED"`).

    Methods:
        get_metrics() -> dict[str, dict[str,object]]:
            Gathers connection details and returns them in a structured dictionary.

        _get_socket_process_map() -> dict[str, dict[str, object]]:
            Maps socket inodes to processes by analyzing `/proc/*/fd/` links.

        _get_process_path(pid: str) -> str:
            Retrieves the full path of a process given a process ID.

        _parse_proc_net_file(
            filepath: pathlib.Path,
            protocol: str,
            family: int,
            inode_proc: dict[str, dict[str, object]]
        ) -> list[dict[str, object]]:
            Parses a given `/proc/net/{tcp,tcp6,udp,udp6}` file to extract active
            connections.

        _parse_ipv4_address(hex_ip: str, hex_port: str) -> str:
            Converts a hexadecimal IPv4 address (in little-endian) and port into a
            human-readable format (IP:port).

        _parse_ipv6_address(hex_ip: str, hex_port: str) -> str:
            Converts a 32-character hexadecimal IPv6 address and a hexadecimal port
            into a human-readable format ([IPv6]:port).
    """

    def __init__(self) -> None:
        """Initializes the NetworkConnectionMonitor class..

        This constructor sets up mappings for TCP connection states and specifies the
        files from which network connection data will be retrieved.

        This constructor sets up the object by initializing:
        - `_TCP_STATES`:
            A dictionary mapping hexadecimal TCP state codes to human-readable
            connection states.

        - `_PROC_FILES`:
            A list of tuples representing `/proc/net` files to monitor.
        """
        self._TCP_STATES = {
            "01": "ESTABLISHED",
            "02": "SYN_SENT",
            "03": "SYN_RECV",
            "04": "FIN_WAIT1",
            "05": "FIN_WAIT2",
            "06": "TIME_WAIT",
            "07": "CLOSE",
            "08": "CLOSE_WAIT",
            "09": "LAST_ACK",
            "0A": "LISTEN",
            "0B": "CLOSING",
        }

        self._PROC_FILES = [
            ("/proc/net/tcp", "tcp", socket.AF_INET),
            ("/proc/net/tcp6", "tcp6", socket.AF_INET6),
            ("/proc/net/udp", "udp", socket.AF_INET),
            ("/proc/net/udp6", "udp6", socket.AF_INET6),
        ]

    def _get_socket_process_map(self) -> dict[str, tuple[str, str]]:
        """Builds a mapping from socket inode to (pid, process name) by scanning all processes' file descriptors.

        This method scans the `/proc` directory for active processes and checks each
        process's file descriptors to find any that correspond to network sockets. For
        each socket, it retrieves the associated PID and process name.

        Returns:
            Dict[str, Tuple[str, str]]:
                A dictionary where the key is the socket inode and value is a tuple
                containing:
                    - `pid` (str): The process ID of the process using the socket.
                    - `process_name` (str): The name of the process using the socket.

                If the process name cannot be determined, the value for `process_name`
                will be an empty string.
        """
        inode_proc = {}
        for pid in filter(str.isdigit, os.listdir("/proc")):
            fd_dir = os.path.join("/proc", pid, "fd")

            try:
                for fd in os.listdir(fd_dir):
                    path = os.path.join(fd_dir, fd)

                    try:
                        target = os.readlink(path)
                        if target.startswith("socket:["):
                            inode = target[8:-1]

                            if inode not in inode_proc:
                                try:
                                    with open(
                                        os.path.join("/proc", pid, "comm"), "r"
                                    ) as f:
                                        proc_name = f.read().strip()
                                except Exception:
                                    proc_name = ""

                                inode_proc[inode] = (pid, proc_name)

                    except Exception:
                        continue

            except Exception:
                continue

        return inode_proc

    def _get_process_path(self, pid: str) -> str:
        """Retrieve the full path to the executable for the given PID.

        Args:
            pid (str):
                The process ID (PID).

        Returns:
            str:
                The full path to the executable or "Unknown Process Path" if it cannot
                be found.
        """
        process_path = "Unknown Process Path"
        exe_path = os.path.join("/proc", pid, "exe")

        try:
            process_path = os.readlink(exe_path)

        except Exception as e:
            logger.debug(
                f"Unable to get full process path for PID: {pid}. Message: {e}"
            )

        return process_path

    def _parse_address(self, hex_ip: str, hex_port: str, family: int) -> str:
        """Converts a hexadecimal IP address (IPv4 or IPv6) and a port into a human-readable format.

        Args:
            hex_ip (str):
                The IP address in hexadecimal format.

            hex_port (str):
                The port number in hexadecimal format.

            family (int):
                The address family. Use socket.AF_INET for IPv4 or socket.AF_INET6 for IPv6.

        Returns:
            str: The formatted address and port, either in the form 'IP:port' or '[IPv6]:port'.

        Raises:
            ValueError:
                - The input hex values are invalid.
                - Addresses are of incorrect length.
                - The address family is unsupported.
                - Errors occur parsing address and port.

            Exception:
                Any unexpected exceptions that occur.
        """
        address = ""
        try:
            if family == socket.AF_INET:
                if len(hex_ip) != 8:
                    raise ValueError(
                        "Invalid IPv4 address length: expected 8 characters, got "
                        f"{len(hex_ip)}"
                    )

                ip_int = int(hex_ip, 16)
                ip_packed = struct.pack("<I", ip_int)
                ip_str = socket.inet_ntoa(ip_packed)

                try:
                    port = int(hex_port, 16)
                except ValueError:
                    raise ValueError(f"Invalid hexadecimal port: {hex_port}")

                address = f"{ip_str}:{port}"

            elif family == socket.AF_INET6:
                if len(hex_ip) != 32:
                    raise ValueError(
                        "Invalid IPv6 address length: expected 32 characters, got "
                        f"{len(hex_ip)}"
                    )

                ip_bytes = bytes.fromhex(hex_ip)
                ip_str = socket.inet_ntop(socket.AF_INET6, ip_bytes)

                try:
                    port = int(hex_port, 16)
                except ValueError:
                    raise ValueError(f"Invalid hexadecimal port: {hex_port}")

                address = f"[{ip_str}]:{port}"

            else:
                raise ValueError(f"Unsupported address family: {family}")

        except ValueError as e:
            raise ValueError(f"Error parsing address or port: {str(e)}")

        except Exception as e:
            raise Exception(f"Unexpected error parsing address or port: {str(e)}")

        return address

    def _parse_proc_net_file(
        self, filepath: pathlib.Path, protocol: str, family: int, inode_proc: dict
    ) -> list[dict]:
        """Parses a /proc/net/{tcp,tcp6,udp,udp6} file and returns a list of network connection details.

        Args:
            filepath (Path):
                Path to the /proc/net/ file to be parsed.

            protocol (str):
                The network protocol (e.g., "tcp", "udp", "tcp6", "udp6").

            family (int):
                Address family (e.g., AF_INET for IPv4, AF_INET6 for IPv6).

            inode_proc (dict[str, dict[str, object]]):
                A mapping of socket inodes to process metadata, typically retrieved
                from `/proc`.

        Returns:
            list[dict[str, Any]]:
                A list of dictionaries, each representing a network connection with
                the following keys:
                    - `protocol` (str):
                        The protocol used (TCP, UDP, etc.).
                    - `local_address` (str):
                        Local IP address and port.
                    - `foreign_address` (str):
                        Remote IP address and port.
                    - `state` (str):
                        Connection state (e.g., "ESTABLISHED", "LISTEN").
                    - `inode` (str):
                        Inode number of the socket.
                    - `pid` (str):
                        Process ID using the connection (if found).
                    - `process` (str):
                        Name of the process using connection.
                    - `process_path` (str):
                        Full path of the process.
                    - `sent_bytes` (int):
                        Number of bytes sent.
                    - `received_bytes` (int):
                        Number of bytes received.

        Raises:
            FileNotFoundError:
                If `/proc/net/{filename}` does not exist.

            IOError:
                If there is an error reading `/proc/net/{filename}`.
        """
        connections = []

        try:
            with open(filepath, "r") as f:
                lines = f.readlines()

        except FileNotFoundError:
            logger.exception(f"File not found: {filepath}")

        except IOError as e:
            logging.exception(f"Error reading file {filepath}: {str(e)}")

        for line in lines[1:]:
            parts = line.split()

            if len(parts) < 10:
                continue

            try:
                local_addr = parts[1]
                rem_addr = parts[2]
                state = parts[3]
                tx_rx = parts[4]
                inode = parts[9]

                local_ip_hex, local_port_hex = local_addr.split(":")
                remote_ip_hex, remote_port_hex = rem_addr.split(":")

                if family not in (socket.AF_INET, socket.AF_INET6):
                    raise ValueError(f"Unsupported address family: {family}")

                local_address = self._parse_address(
                    hex_ip=local_ip_hex, hex_port=local_port_hex, family=family
                )
                foreign_address = self._parse_address(
                    hex_ip=remote_ip_hex, hex_port=remote_port_hex, family=family
                )

                tx_queue_hex, rx_queue_hex = tx_rx.split(":")
                send_bytes = int(tx_queue_hex, 16)
                received_bytes = int(rx_queue_hex, 16)

                if protocol in ("tcp", "tcp6"):
                    state_str = self._TCP_STATES.get(state, state)
                else:
                    state_str = "N/A"

                if "tcp" in protocol:
                    protocol_str = "TCP"
                elif "udp" in protocol:
                    protocol_str = "UDP"
                else:
                    protocol_str = protocol

                pid, proc_name = inode_proc.get(inode, ("-", "-"))

                try:
                    process_path = self._get_process_path(pid)
                except Exception:
                    process_path = "Unknown Process Path"

                connections.append(
                    {
                        "pid": pid,
                        "process": proc_name,
                        "process_path": process_path,
                        "protocol": protocol_str,
                        "state": state_str,
                        "local_address": local_address,
                        "foreign_address": foreign_address,
                        "sent_bytes": send_bytes,
                        "received_bytes": received_bytes,
                        "inode": inode,
                    }
                )

            except ValueError as e:
                logger.exception(
                    f"Skipping line in `{filepath}` due to error: {str(e)}"
                )
                continue

            except Exception as e:
                logger.exception(f"Error processing line: {str(e)}")
                continue

        return connections

    def get_metrics(self) -> dict[str, dict[str, object]]:
        """Gather connection information from various `/proc/net` files and return a dictionary.

        This method parses the network connection data available in the `/proc/net`
        files (e.g., tcp, udp) to extract details about active network connections,
        including the protocol, local and foreign addresses, send/receive byte counts,
        the inode, and the associated process information (PID and name). Each
        connection is uniquely identified by an MD5 hash of the 5-tuple of the
        connection's protocol, local and remote addresses, and ports.

        Returns:
            dict[str, dict[str, object]]:
                A dictionary where each key is an MD5 hash of the 5-tuple (protocol,
                local IP, local port, remote IP, remote port) and the value is a
                dictionary containing connection details, such as:

                    - `protocol` (str):
                        Connection protocol, e.g., "tcp", "udp".
                    - `state` (str):
                        State of the connection, e.g., "ESTABLISHED".
                    - `local_address` (str):
                        Local IP address and port.
                    - `foreign_address` (str):
                        Remote IP address and port.
                    - `sent_bytes` (int):
                        Bytes sent over the connection.
                    - `received_bytes` (int):
                        Bytes received over the connection.
                    - `inode` (str):
                        The inode identifier for the connection.
                    - `pid` (str):
                        The ID of the process associated with the connection.
                    - `process` (str):
                        The name of the process associated with the connection.
                    - `process_path` (str):
                        The absolute path of the process.

        Example:
                {
                    "<hash_for_connection_1>": {
                        "protocol": "tcp",
                        "state": "ESTABLISHED",
                        "local_address": "127.0.0.1:1234",
                        "foreign_address": "8.8.8.8:80",
                        "sent_bytes": 0,
                        "received_bytes": 0,
                        "inode": "123456",
                        "pid": "1234",
                        "process": "process_name"
                    },
                    "<hash_for_connection_2>": { ... },
                    ...
                }
        """
        connections = {}
        inode_proc = self._get_socket_process_map()

        for file_path, protocol, family in self._PROC_FILES:
            if os.path.exists(file_path):
                for conn in self._parse_proc_net_file(
                    file_path, protocol, family, inode_proc
                ):
                    try:
                        local_ip, local_port = conn["local_address"].rsplit(":", 1)
                        remote_ip, remote_port = conn["foreign_address"].rsplit(":", 1)

                    except Exception:
                        local_ip, local_port = conn.get("local_address", ""), ""
                        remote_ip, remote_port = conn.get("foreign_address", ""), ""

                    five_tuple = (
                        f"{conn.get('protocol', '')}"
                        f"|{local_ip}"
                        f"|{local_port}"
                        f"|{remote_ip}"
                        f"|{remote_port}"
                    )
                    key = hashlib.md5(five_tuple.encode()).hexdigest()

                    connections[key] = {
                        "protocol": conn.get("protocol"),
                        "state": conn.get("state"),
                        "local_address": conn.get("local_address"),
                        "foreign_address": conn.get("foreign_address"),
                        "sent_bytes": conn.get("sent_bytes"),
                        "received_bytes": conn.get("received_bytes"),
                        "inode": conn.get("inode"),
                        "pid": conn.get("pid"),
                        "process": conn.get("process"),
                        "process_path": conn.get("process_path"),
                    }

        return connections
