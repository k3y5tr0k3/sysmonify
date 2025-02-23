(function($) {
    'use strict';
    $(function() {
        let networkDetails;
        let networkStats;
        let networkConnections;
        let sortedFilteredNetworkConnections;
        let selectedNetworkInterfaceName;

        let networkUsageChart;
        let networkUsageChartDatasets = [
            {
                label: "Transmission Speed (TX)",
                data: Array(60).fill(0.00),
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1.5,
                fill: false,
                pointRadius: 0,
            },
            {
                label: "Receive Speed (RX)",
                data: Array(60).fill(0.00),
                backgroundColor: "rgba(153, 102, 255, 0.2)",
                borderColor: "rgba(153, 102, 255, 1)",
                borderWidth: 1.5,
                fill: false,
                pointRadius: 0,
            }
        ];
        let networkUsageChartLabels = Array(60).fill("");

        let packetDropChart;
        let packetDropChartDatasets = [
            {
                label: "Dropped Transmission Packet",
                data: Array(60).fill(0.00),
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1.5,
                fill: false,
                pointRadius: 0,
            },
            {
                label: "Dropped Receive Packet",
                data: Array(60).fill(0.00),
                backgroundColor: "rgba(153, 102, 255, 0.2)",
                borderColor: "rgba(153, 102, 255, 1)",
                borderWidth: 1.5,
                fill: false,
                pointRadius: 0,
            }
        ];
        let packetDropChartLabels = Array(60).fill("");

        const networkConnectionsTableSort = {
            columnName: "pid",
            value: null,
        }

        const networkConnectionsTableFilter = {
            columnName: null,
            value: null
        }

        const tcpStates = new Set([
            "ESTABLISHED",
            "SYN_SENT",
            "SYN_RECV",
            "FIN_WAIT1",
            "FIN_WAIT2",
            "TIME_WAIT",
            "CLOSE",
            "CLOSE_WAIT",
            "LAST_ACK",
            "LISTEN",
            "CLOSING"
        ]);

        const networkConnectionsFilterKeys = new Set([
            "pid",
            "process",
            "state",
            "protocol"
        ]);

        const networkConnectionsSortKeys = new Set([
            "pid",
            "process",
            "protocol",
            "state",
            "local_address",
            "foreign_address"
        ]);

        const filterColumnsSelect = document.getElementById("filterColumns");
        const filterValueSelect = document.getElementById("filterValues");
        const sortColumnsSelect = document.getElementById("sortColumns");
        const sortAscendingCheck = document.getElementById("ascending");

        let uniqueConnectionsValues;

        const tabs = document.getElementsByClassName("tab-link");
        const tabPanes = document.getElementsByClassName("tab-pane");
        const networkConnectionTableBody = document.getElementById("networkConnectionTableBody");

        if ($("#networkChart").length) {
            const ctx = document.getElementById('networkChart');

            networkUsageChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: networkUsageChartLabels,
                    datasets: networkUsageChartDatasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    elements: {
                        line: {
                            tension: 0.3,
                        }
                    },
                    scales: {
                        y: {
                            min: 0,
                            grid: {
                                display: true,
                                color:"#F0F0F0",
                                drawBorder: false,
                            },
                            ticks: {
                                beginAtZero: false,
                                autoSkip: true,
                                maxTicksLimit: 4,
                                color:"#6B778C",
                                font: { size: 10 },
                                stepSize: 0.01,
                            },
                            title: {
                                display: true,
                                text: "RX/TX (MB/s)",
                            }
                        },
                        x: {
                            grid: { display: false, drawBorder: false },
                            ticks: {
                                beginAtZero: false,
                                autoSkip: true,
                                maxTicksLimit: 7,
                                color:"#6B778C",
                                font: { size: 10 }
                            }
                        }
                    },
                    animation: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            usePointStyle: true,
                            labels: {
                                boxWidth: 10,
                                padding: 10
                            }
                        },
                        tooltip: {
                            enabled: true,
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            titleFont: {
                                size: 14,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 8
                            },
                        }
                    }
                }
            });
        }

        if ($("#packetDropChart").length) {
            const ctx = document.getElementById('packetDropChart');

            packetDropChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: packetDropChartLabels,
                    datasets: packetDropChartDatasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    elements: {
                        line: {
                            tension: 0.3,
                        }
                    },
                    scales: {
                        y: {
                            min: 0,
                            grid: {
                                display: true,
                                color:"#F0F0F0",
                                drawBorder: false,
                            },
                            ticks: {
                                beginAtZero: false,
                                autoSkip: true,
                                maxTicksLimit: 4,
                                color:"#6B778C",
                                font: { size: 10 },
                                stepSize: 1,
                            },
                            title: {
                                display: true,
                                text: "# of Dropped Packets",
                            }
                        },
                        x: {
                            grid: { display: false, drawBorder: false },
                            ticks: {
                                beginAtZero: false,
                                autoSkip: true,
                                maxTicksLimit: 7,
                                color:"#6B778C",
                                font: { size: 10 }
                            }
                        }
                    },
                    animation: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            usePointStyle: true,
                            labels: {
                                boxWidth: 10,
                                padding: 10
                            }
                        },
                        tooltip: {
                            enabled: true,
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            titleFont: {
                                size: 14,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 8
                            },
                        }
                    }
                }
            });
        }

        Array.from(tabs).forEach(tab => {
            tab.addEventListener('click', function(event) {
                event.preventDefault();

                Array.from(tabs).forEach(t => t.classList.remove('active', 'show'));
                Array.from(tabPanes).forEach(pane => pane.classList.remove('active', 'show'));

                tab.classList.add('active', 'show');

                const targetPaneID = tab.getAttribute('aria-controls');

                const targetPane = document.getElementById(targetPaneID);
                if (targetPane) {
                    targetPane.classList.add('active', 'show');
                }
            });
        });

        const socket = new WebSocket('ws://' + window.location.host + '/ws/network/');

        socket.onopen = function(e) {
            console.log("Successfully connected to WebSocket.");
        };

        socket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly.');
        };

        socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            console.log(data);

            if (data) {
                if (data.details) {
                    networkDetails = data.details;
                    await updateNetworkInterfaceChoiceDropdownItemsAsync();
                    await updateNetworkInterfaceDetailsAsync();
                }

                if (data.stats) {
                    networkStats = data.stats;
                    await updateUsageNetworkChartAsync();
                    await updatePacketDropChartAsync();
                }

                if (data.connections) {
                    networkConnections = data.connections;
                    await filterNetworkConnectionsAsync();
                    await updateNetworkConnectionTableAsync();
                    await updateConnectionsTableFilterOptions();
                }
            }
        };

        async function updateNetworkInterfaceChoiceDropdownItemsAsync() {
            return new Promise((resolve, reject) => {
                try {
                    const dropdownMenu = document.querySelector('.dropdown-menu');
                    const dropDownMenuButtonText = document.getElementById("dropDownButtonText");
                    dropdownMenu.innerHTML = '';

                    Object.keys(networkDetails).forEach((key, index) => {
                        let interfaceName = key;
                        const newItem = document.createElement('a');
                        newItem.classList.add('dropdown-item');
                        newItem.href = '#';
                        newItem.textContent = `${index}: ${interfaceName}`;
                        newItem.setAttribute("data-index", interfaceName);
                        dropdownMenu.appendChild(newItem);

                        newItem.addEventListener('click', (event) => {
                            const interfaceName = event.target.getAttribute('data-index');
                            const dropDownItemText = event.target.innerText;

                            selectedNetworkInterfaceName = interfaceName;
                            dropDownMenuButtonText.innerText = dropDownItemText;
                            diskUtilDatasets = Array(60).fill(0.00);
                            diskUtilLabels = Array(60).fill("");
                        });
                    });

                    let interfaceName = Object.keys(networkDetails)[0];
                    dropDownMenuButtonText.innerText = `0: ${interfaceName}`;
                    selectedNetworkInterfaceName = interfaceName;

                    resolve();
                } catch (error) {
                    console.error("Error updating dropdown content:", error);
                    reject(error);
                }
            });
        }

        async function updateNetworkInterfaceDetailsAsync() {
            return new Promise((resolve, reject) => {
                try {
                    let maxLinkSpeed = networkDetails[selectedNetworkInterfaceName].speed;
                    let mtu = networkDetails[selectedNetworkInterfaceName].mtu;
                    let maxLinkSpeedText;
                    let mtuText;

                    if (maxLinkSpeed != "Unknown") {
                        maxLinkSpeedText = `${maxLinkSpeed} MB/s`;
                    } else {
                        maxLinkSpeedText = maxLinkSpeed;
                    }

                    if (mtu != "Unknown"){
                        mtuText = `${mtu} Bytes`;
                    } else {
                        mtuText = mtu;
                    }

                    console.log(networkDetails[selectedNetworkInterfaceName]);
                    document.getElementById("interfaceType").innerText = networkDetails[selectedNetworkInterfaceName].type;
                    document.getElementById("interfaceMAC").innerText = networkDetails[selectedNetworkInterfaceName].mac;
                    document.getElementById("interfaceIPv4").innerText = networkDetails[selectedNetworkInterfaceName].ipv4;
                    document.getElementById("interfaceIPv6").innerText = networkDetails[selectedNetworkInterfaceName].ipv6;
                    document.getElementById("interfaceMaxLinkSpeed").innerText = maxLinkSpeedText;
                    document.getElementById("interfaceMTU").innerText = mtuText;

                    resolve();
                } catch (error) {
                    console.error("Error updating interface details:", error);
                    reject(error);
                }
            });
        }

        async function updateUsageNetworkChartAsync() {
            return new Promise((resolve, reject) => {
                try {
                    if (networkStats[selectedNetworkInterfaceName]) {
                        let tx = networkStats[selectedNetworkInterfaceName].tx_mbps.toFixed(2);
                        let rx = networkStats[selectedNetworkInterfaceName].rx_mbps.toFixed(2);
                        let now = new Date().toLocaleTimeString();

                        if (networkUsageChartLabels.length >= 60) {
                            networkUsageChartLabels.shift();
                            networkUsageChartDatasets[0].data.shift();
                            networkUsageChartDatasets[1].data.shift();
                        }

                        networkUsageChartLabels.push(now);
                        networkUsageChartDatasets[0].data.push(tx);
                        networkUsageChartDatasets[1].data.push(rx);

                        networkUsageChart.update();

                        networkChartText.innerText = `TX ${tx} MB/s - RX ${rx} MB/s`;
                    }

                    resolve();
                } catch (error) {
                    console.error("Error updating network usage chart:", error);
                    reject(error);
                }
            });
        }

        async function updatePacketDropChartAsync() {
            return new Promise((resolve, reject) => {
                try {
                    if (networkStats[selectedNetworkInterfaceName]) {
                        let tx_drop = networkStats[selectedNetworkInterfaceName].tx_dropped;
                        let rx_drop = networkStats[selectedNetworkInterfaceName].rx_dropped;
                        let now = new Date().toLocaleTimeString();

                        if (packetDropChartLabels.length >= 60) {
                            packetDropChartLabels.shift();
                            packetDropChartDatasets[0].data.shift();
                            packetDropChartDatasets[1].data.shift();
                        }

                        packetDropChartLabels.push(now);
                        packetDropChartDatasets[0].data.push(tx_drop);
                        packetDropChartDatasets[1].data.push(rx_drop);

                        packetDropChart.update();
                    }

                    resolve();
                } catch (error) {
                    console.error("Error updating dropped packet chart:", error);
                    reject(error);
                }
            });
        }

        async function updateNetworkConnectionTableAsync() {
            return new Promise((resolve, reject) => {
                try {
                    networkConnectionTableBody.innerHTML = "";

                    let connections = Object.values(sortedFilteredNetworkConnections);

                    connections.forEach(conn => {
                        let row = document.createElement("tr");

                        let pidCell = document.createElement("td");
                        pidCell.textContent = conn.pid;
                        row.appendChild(pidCell);

                        let processCell = document.createElement("td");
                        processCell.textContent = conn.process;
                        row.appendChild(processCell);

                        let protocolCell = document.createElement("td");
                        protocolCell.textContent = conn.protocol;
                        row.appendChild(protocolCell);

                        let stateCell = document.createElement("td");
                        stateCell.textContent = conn.state;
                        row.appendChild(stateCell);

                        let localAddrCell = document.createElement("td");
                        localAddrCell.textContent = conn.local_address;
                        row.appendChild(localAddrCell);

                        let foreignAddrCell = document.createElement("td");
                        foreignAddrCell.textContent = conn.foreign_address;
                        row.appendChild(foreignAddrCell);

                        let sentBytesCell = document.createElement("td");
                        sentBytesCell.textContent = conn.sent_bytes;
                        row.appendChild(sentBytesCell);

                        let receivedBytesCell = document.createElement("td");
                        receivedBytesCell.textContent = conn.received_bytes;
                        row.appendChild(receivedBytesCell);

                        networkConnectionTableBody.appendChild(row);
                    });

                    resolve();
                } catch (error) {
                    console.error("Error update network connection table:", error);
                    reject(error);
                }
            });
        }

        async function filterNetworkConnectionsAsync() {
            await new Promise((resolve, reject) => {
                try {
                    const connections = Object.values(networkConnections);
                    const filterColumnName = networkConnectionsTableFilter.columnName;
                    const filterValue = networkConnectionsTableFilter.value;
                    const sortBy = networkConnectionsTableSort.columnName;
                    const ascending = networkConnectionsTableSort.ascending;
                    let filteredNetworkConnections;

                    if (filterValue !== null) {
                        filteredNetworkConnections = Object.fromEntries(
                            Object.entries(connections).filter(
                                ([key, value]) => value[filterColumnName] === filterValue
                            )
                        );
                    } else {
                        filteredNetworkConnections = networkConnections;
                    }

                    sortedFilteredNetworkConnections = Object.values(filteredNetworkConnections).sort((a, b) => {
                        if (sortBy === 'pid') {
                            const pidA = isNaN(parseInt(a.pid)) ? -Infinity : parseInt(a.pid);
                            const pidB = isNaN(parseInt(b.pid)) ? -Infinity : parseInt(b.pid);

                            return ascending ? pidA - pidB : pidB - pidA;
                        }
                        else if (sortBy === 'process') {
                            return ascending ? a.process.localeCompare(b.process) : b.process.localeCompare(a.process);
                        }
                        else if (sortBy === 'protocol') {
                            return ascending ? a.protocol.localeCompare(b.protocol) : b.protocol.localeCompare(a.protocol);
                        }
                        else if (sortBy === 'state') {
                            return ascending ? a.state.localeCompare(b.state) : b.state.localeCompare(a.state);
                        }
                        else if (sortBy === 'local_address') {
                            return ascending ? a.local_address.localeCompare(b.local_address) : b.local_address.localeCompare(a.local_address);
                        }
                        else if (sortBy === 'foreign_address') {
                            return ascending ? a.foreign_address.localeCompare(b.foreign_address) : b.foreign_address.localeCompare(a.foreign_address);
                        }
                    });

                    console.log("Sorted and filtered connections: ", sortedFilteredNetworkConnections);

                    resolve();
                } catch (error) {
                    console.log("Error when applying filters to network connections: ", error);
                    reject();
                }
            });
        }

        async function updateConnectionsTableFilterOptions() {
            await new Promise((resolve, reject) => {
                try {
                    uniqueConnectionsValues = {};
                    networkConnectionsFilterKeys.forEach(key => {
                        uniqueConnectionsValues[key] = getUniqueConnectionsValuesByKey(key);
                    });

                    filterColumnsSelect.innerHTML = "";
                    sortColumnsSelect.innerHTML = "";

                    networkConnectionsFilterKeys.forEach(key => {
                        const filterColumnOption = document.createElement("option");
                        filterColumnOption.setAttribute("value", key);
                        filterColumnOption.textContent = key;
                        filterColumnsSelect.appendChild(filterColumnOption);
                    });

                    networkConnectionsSortKeys.forEach(key => {
                        const sortColumnOption = document.createElement("option");
                        sortColumnOption.setAttribute("value", key);
                        sortColumnOption.textContent = key;
                        sortColumnsSelect.appendChild(sortColumnOption);
                    });

                    filterColumnsSelect.value = networkConnectionsTableFilter.columnName;
                    filterValueSelect.value = networkConnectionsTableFilter.value;

                    resolve();
                } catch (error) {
                    console.error("Error occurred while updating connections table filter options: ", error);
                    reject();
                }
            });
        }

        async function updateConnectionsTableFilterValues() {
            await new Promise((resolve, reject) => {
                try {
                    const filterColumn = networkConnectionsTableFilter.columnName;
                    filterValueSelect.innerHTML = "";

                    uniqueConnectionsValues[filterColumn].forEach(value => {
                        const filterValueOption = document.createElement("option");
                        filterValueOption.setAttribute("value", value);
                        filterValueOption.textContent = value;
                        filterValueSelect.appendChild(filterValueOption);
                    });

                    filterValueSelect.removeAttribute('disabled');

                    resolve();
                } catch (error) {
                    console.error("Error occurred while updating connections table filter options: ", error);
                    reject();
                }
            });
        }

        function getUniqueConnectionsValuesByKey(key) {
            const uniqueValues = new Set();

            for (const obj of Object.values(networkConnections)) {
                const value = obj[key];
                if (!uniqueValues.has(value)) {
                    uniqueValues.add(value);
                }
            }

            return uniqueValues;
        }

        filterColumnsSelect.addEventListener('change', async (event) => {
            networkConnectionsTableFilter.columnName = event.target.value;
            networkConnectionsTableFilter.value = null;
            filterValueSelect.value = null;
            await updateConnectionsTableFilterValues();
            await updateNetworkConnectionTableAsync();
        });

        filterValueSelect.addEventListener('change', async (event) => {
            networkConnectionsTableFilter.value = event.target.value;
            await filterNetworkConnections();
            await updateNetworkConnectionTableAsync();
        });

        sortColumnsSelect.addEventListener('change', async (event) => {
            networkConnectionsTableSort.columnName = event.target.value;
            await filterNetworkConnections();
            await updateNetworkConnectionTableAsync();
        });

        sortAscendingCheck.addEventListener('change', async (event) => {
            networkConnectionsTableSort.ascending = event.target.checked;
            await filterNetworkConnections();
            await updateNetworkConnectionTableAsync();
        });
    });
})(jQuery);
