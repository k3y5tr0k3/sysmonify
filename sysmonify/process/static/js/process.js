(function($) {
    'use strict';
    $(function() {
        let processes;
        let uniqueProcessValues;
        let sortedFilteredProcesses;
        const processesTableBody = document.getElementById("processesTableBody");
        const processCountText = document.getElementById("totalProcessesText");

        const processTableSort = {
            columnName: "pid",
            value: null,
        }

        const processTableFilter = {
            columnName: null,
            value: null
        }

        const processFilterKeys = new Set([
            "pid",
            "command",
            "user",
        ]);

        const processSortKeys = new Set([
            "pid",
            "command",
            "user",
            "memory",
            "cpu",
            "up_time"
        ]);

        const filterColumnsSelect = document.getElementById("filterColumns");
        const filterValueSelect = document.getElementById("filterValues");
        const sortColumnsSelect = document.getElementById("sortColumns");
        const sortAscendingCheck = document.getElementById("ascending");

        const socket = new WebSocket('ws://' + window.location.host + '/ws/processes/');

        socket.onopen = function(e) {
            console.log("Successfully connected to WebSocket.");
        };

        socket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly.');
        };

        socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            if (data) {
                if (data.metrics) {
                    processes = data.metrics;
                    await filterProcessesAsync();
                    await updateProcessTableAsync();
                    await updateProcessTableFilterOptions();
                }
            }
        };

        async function updateProcessTableAsync() {
            return new Promise((resolve, reject) => {
                try {
                    processesTableBody.innerHTML = "";

                    let processes_list = Object.values(sortedFilteredProcesses);

                    processes_list.forEach(proc => {
                        let row = document.createElement("tr");

                        let pidCell = document.createElement("td");
                        pidCell.textContent = proc.pid;
                        row.appendChild(pidCell);

                        let userCell = document.createElement("td");
                        userCell.textContent = proc.user;
                        row.appendChild(userCell);

                        let commandCell = document.createElement("td");
                        commandCell.textContent = proc.command;
                        commandCell.classList.add("text-truncate");
                        row.appendChild(commandCell);

                        let cpuCell = document.createElement("td");
                        let cpuTextParent = document.createElement("div");
                        cpuTextParent.classList.add("d-flex", "justify-content-between", "align-items-center", "mb-1", "max-width-progress-wrap");
                        let cpuTextChild = document.createElement("p");
                        cpuTextChild.textContent = `${proc.cpu}%`
                        cpuTextChild.classList.add("text-success");
                        cpuTextParent.appendChild(cpuTextChild);
                        cpuCell.appendChild(cpuTextParent);
                        let cpuProgressBarParent = document.createElement("div");
                        cpuProgressBarParent.classList.add("progress", "progress-md");
                        let cpuProgressBarChild = document.createElement("div");
                        cpuProgressBarChild.classList.add("progress-bar", "bg-success");
                        cpuProgressBarChild.setAttribute("role", "progressbar");
                        cpuProgressBarChild.setAttribute("style", `width: ${proc.cpu}%`);
                        cpuProgressBarChild.setAttribute("aria-valuenow", proc.cpu);
                        cpuProgressBarChild.setAttribute("aria-valuemin", 0);
                        cpuProgressBarChild.setAttribute("aria-valuemax", 100);
                        cpuProgressBarParent.appendChild(cpuProgressBarChild);
                        cpuCell.appendChild(cpuProgressBarParent);
                        row.appendChild(cpuCell);

                        let memoryCell = document.createElement("td");
                        let memoryTextParent = document.createElement("div");
                        memoryTextParent.classList.add("d-flex", "justify-content-between", "align-items-center", "mb-1", "max-width-progress-wrap");
                        let memoryTextChild = document.createElement("p");
                        memoryTextChild.textContent = `${proc.memory}%`
                        memoryTextChild.classList.add("text-success");
                        memoryTextParent.appendChild(memoryTextChild);
                        memoryCell.appendChild(memoryTextParent);
                        let memoryProgressBarParent = document.createElement("div");
                        memoryProgressBarParent.classList.add("progress", "progress-md");
                        let memoryProgressBarChild = document.createElement("div");
                        memoryProgressBarChild.classList.add("progress-bar", "bg-success");
                        memoryProgressBarChild.setAttribute("role", "progressbar");
                        memoryProgressBarChild.setAttribute("style", `width: ${proc.memory}%`);
                        memoryProgressBarChild.setAttribute("aria-valuenow", proc.memory);
                        memoryProgressBarChild.setAttribute("aria-valuemin", 0);
                        memoryProgressBarChild.setAttribute("aria-valuemax", 100);
                        memoryProgressBarParent.appendChild(memoryProgressBarChild);
                        memoryCell.appendChild(memoryProgressBarParent);
                        row.appendChild(memoryCell);

                        let upTimeCell = document.createElement("td");
                        upTimeCell.textContent = proc.up_time;
                        row.appendChild(upTimeCell);

                        processesTableBody.appendChild(row);
                    });

                    processCountText.textContent = `Total Processes: ${Object.keys(processes).length}`;

                    resolve();
                } catch (error) {
                    console.error("Error updating process table:", error);
                    reject(error);
                }
            });
        }

        async function filterProcessesAsync() {
            await new Promise((resolve, reject) => {
                try {
                    const processes_list = Object.entries(processes).map(([pid, processInfo]) => ({
                        pid,
                        ...processInfo
                    }));
                    const filterColumnName = processTableFilter.columnName;
                    const filterValue = processTableFilter.value;
                    const sortBy = processTableSort.columnName;
                    const ascending = processTableSort.ascending;
                    let filteredProcesses;

                    if (filterValue !== null) {
                        filteredProcesses = Object.fromEntries(
                            Object.entries(processes_list).filter(
                                ([key, value]) => value[filterColumnName] === filterValue
                            )
                        );
                    } else {
                        filteredProcesses = processes_list;
                    }

                    sortedFilteredProcesses = Object.values(filteredProcesses).sort((a, b) => {
                        if (sortBy === 'pid') {
                            const pidA = isNaN(parseInt(a.pid)) ? -Infinity : parseInt(a.pid);
                            const pidB = isNaN(parseInt(b.pid)) ? -Infinity : parseInt(b.pid);

                            return ascending ? pidA - pidB : pidB - pidA;
                        }
                        else if (['command', 'user'].includes(sortBy)) {
                            return ascending ? a[sortBy].localeCompare(b[sortBy]) : b[sortBy].localeCompare(a[sortBy]);
                        }
                        else if (['cpu', 'memory'].includes(sortBy)) {
                            const numA = parseFloat(a[sortBy]) || 0;
                            const numB = parseFloat(b[sortBy]) || 0;
                            return ascending ? numA - numB : numB - numA;
                        }
                        else if (sortBy === 'up_time') {
                            const timeA = convertTimeToSeconds(a.up_time);
                            const timeB = convertTimeToSeconds(b.up_time);
                            return ascending ? timeA - timeB : timeB - timeA;
                        }
                    });

                    resolve();
                } catch (error) {
                    console.log("Error when applying filters to processes: ", error);
                    reject();
                }
            });
        }

        async function updateProcessTableFilterOptions() {
            await new Promise((resolve, reject) => {
                try {
                    uniqueProcessValues = {};
                    processFilterKeys.forEach(key => {
                        uniqueProcessValues[key] = getUniqueConnectionsValuesByKey(key);
                    });

                    filterColumnsSelect.innerHTML = "";
                    sortColumnsSelect.innerHTML = "";

                    processFilterKeys.forEach(key => {
                        const filterColumnOption = document.createElement("option");
                        filterColumnOption.setAttribute("value", key);
                        filterColumnOption.textContent = key;
                        filterColumnsSelect.appendChild(filterColumnOption);
                    });

                    processSortKeys.forEach(key => {
                        const sortColumnOption = document.createElement("option");
                        sortColumnOption.setAttribute("value", key);
                        sortColumnOption.textContent = key;
                        sortColumnsSelect.appendChild(sortColumnOption);
                    });

                    filterColumnsSelect.value = processTableFilter.columnName;
                    filterValueSelect.value = processTableFilter.value;

                    resolve();
                } catch (error) {
                    console.error("Error occurred while updating process table filter options: ", error);
                    reject();
                }
            });
        }

        async function updateProcessTableFilterValues() {
            await new Promise((resolve, reject) => {
                try {
                    const filterColumn = processTableFilter.columnName;
                    filterValueSelect.innerHTML = "";

                    uniqueProcessValues[filterColumn].forEach(value => {
                        const filterValueOption = document.createElement("option");
                        filterValueOption.setAttribute("value", value);
                        filterValueOption.textContent = value;
                        filterValueSelect.appendChild(filterValueOption);
                    });

                    filterValueSelect.removeAttribute('disabled');

                    resolve();
                } catch (error) {
                    console.error("Error occurred while updating process table filter values: ", error);
                    reject();
                }
            });
        }

        function getUniqueConnectionsValuesByKey(key) {
            const uniqueValues = new Set();

            for (const obj of Object.values(processes)) {
                const value = obj[key];
                if (!uniqueValues.has(value)) {
                    uniqueValues.add(value);
                }
            }

            return uniqueValues;
        }

        filterColumnsSelect.addEventListener('change', async (event) => {
            processTableFilter.columnName = event.target.value;
            processTableFilter.value = null;
            filterValueSelect.value = null;
            await updateProcessTableFilterValues();
            await updateProcessTableAsync();
        });

        filterValueSelect.addEventListener('change', async (event) => {
            processTableFilter.value = event.target.value;
            await filterProcessesAsync();
            await updateProcessTableAsync();
        });

        sortColumnsSelect.addEventListener('change', async (event) => {
            processTableSort.columnName = event.target.value;
            await filterProcessesAsync();
            await updateProcessTableAsync();
        });

        sortAscendingCheck.addEventListener('change', async (event) => {
            processTableSort.ascending = event.target.checked;
            await filterProcessesAsync();
            await updateProcessTableAsync();
        });
    });
})(jQuery);
