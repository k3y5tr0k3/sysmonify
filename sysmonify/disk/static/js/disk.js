(function($) {
    'use strict';
    $(function() {
        let disks;
        let disksSpeeds;
        let selectedDisk = 0;
        const dropDownMenuButton = document.getElementById("dropDownButtonText");

        let diskUtilChart;
        let diskUtilLabels = Array(60).fill("");
        let diskUtilDatasets = [
            {
                label: "Read Speed",
                data: Array(60).fill(0.00),
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1.5,
                fill: false,
                pointRadius: 0,
            },
            {
                label: "Write Speed",
                data: Array(60).fill(0.00),
                backgroundColor: "rgba(153, 102, 255, 0.2)",
                borderColor: "rgba(153, 102, 255, 1)",
                borderWidth: 1.5,
                fill: false,
                pointRadius: 0,
            }
        ];
        let diskUtilText = document.getElementById("diskUtilText");

        var graphGradient = document.getElementById("diskUtilizationChart").getContext('2d');
        var graphGradient2 = document.getElementById("diskUtilizationChart").getContext('2d');
        var saleGradientBg = graphGradient.createLinearGradient(5, 0, 5, 100);
        saleGradientBg.addColorStop(0, 'rgba(26, 115, 232, 0.18)');
        saleGradientBg.addColorStop(1, 'rgba(26, 115, 232, 0.02)');
        var saleGradientBg2 = graphGradient2.createLinearGradient(100, 0, 50, 150);
        saleGradientBg2.addColorStop(0, 'rgba(0, 208, 255, 0.19)');
        saleGradientBg2.addColorStop(1, 'rgba(0, 208, 255, 0.03)');

        if ($("#diskUtilizationChart").length) {
            const ctx = document.getElementById('diskUtilizationChart');

            diskUtilChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: diskUtilLabels,
                    datasets: diskUtilDatasets
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
                                font: { size: 10 }
                            },
                            title: {
                                display: true,
                                text: "Read/Write (MB/s)",
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

        const socket = new WebSocket('ws://' + window.location.host + '/ws/disks/');

        socket.onopen = function(e) {
            console.log("Successfully connected to WebSocket.");
        };

        socket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly.');
        };

        socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            console.log(data);


            if (data){
                if (data.disks) {
                    disks = data.disks
                    await updateDiskDetailsAsync();
                    await updateDiskChoiceDropdownItemsAsync();
                    await updateDiskPartitionTableAsync();
                }

                if (data.disks_speeds) {
                    disksSpeeds = data.disks_speeds
                    await updateDiskUtilChartAsync();
                }
            }
        };

        async function updateDiskUtilChartAsync() {
            return new Promise((resolve, reject) => {
                try {
                    let selectedDiskName = disks[selectedDisk].name;
                    let diskSpeed = disksSpeeds[selectedDiskName];
                    let now = new Date().toLocaleTimeString();

                    if (diskSpeed) {
                        let readSpeed = diskSpeed.read_speed.toFixed(2);;
                        let writeSpeed = diskSpeed.write_speed.toFixed(2);;

                        if (diskUtilLabels.length >= 60) {
                            diskUtilLabels.shift();
                            diskUtilDatasets[0].data.shift();
                            diskUtilDatasets[1].data.shift();
                        }

                        diskUtilLabels.push(now);
                        diskUtilDatasets[0].data.push(readSpeed);
                        diskUtilDatasets[1].data.push(writeSpeed);

                        diskUtilChart.update();

                        diskUtilText.innerText = `Read ${readSpeed} MB/s - Write ${writeSpeed} MB/s`;

                        console.log(diskUtilDatasets);
                    }

                    resolve();
                } catch (error) {
                    console.error("Error updating utilization chart:", error);
                    reject(error);
                }
            });
        }

        async function updateDiskDetailsAsync() {
            return new Promise((resolve, reject) => {
                try {
                    document.getElementById("vendor").innerText = disks[selectedDisk].vendor;
                    document.getElementById("model").innerText = disks[selectedDisk].model;
                    document.getElementById("diskType").innerText = disks[selectedDisk].tran;
                    document.getElementById("serial").innerText = disks[selectedDisk].serial;
                    document.getElementById("diskSize").innerText = disks[selectedDisk].size;
                    document.getElementById("partitionScheme").innerText = disks[selectedDisk].pttype;

                    resolve();
                } catch (error) {
                    console.error("Error updating utilization chart:", error);
                    reject(error);
                }
            });
        }

        async function updateDiskChoiceDropdownItemsAsync() {
            return new Promise((resolve, reject) => {
                try {
                    const dropdownMenu = document.querySelector('.dropdown-menu');
                    dropdownMenu.innerHTML = '';

                    disks.forEach((disk, index) => {
                        const newItem = document.createElement('a');
                        newItem.classList.add('dropdown-item');
                        newItem.href = '#';
                        newItem.textContent = `${disk.name}: ${disk.model}(${disk.serial})`;
                        newItem.setAttribute("data-index", index);
                        dropdownMenu.appendChild(newItem);

                        newItem.addEventListener('click', (event) => {
                            const index = event.target.getAttribute('data-index');

                            selectedDisk = index;
                            dropDownMenuButton.innerText = `${disks[index].name}: ${disks[index].model}(${disks[index].serial})`;
                            diskUtilDatasets[0].data = Array(60).fill(0.00);
                            diskUtilDatasets[1].data = Array(60).fill(0.00);
                            diskUtilLabels = Array(60).fill("");
                        });
                    });

                    dropDownMenuButton.innerText = `${disks[selectedDisk].name}: ${disks[selectedDisk].model}(${disks[selectedDisk].serial})`;

                    resolve();
                } catch (error) {
                    console.error("Error updating dropdown content:", error);
                    reject(error);
                }
            });
        }

        async function updateDiskPartitionTableAsync() {
            return new Promise((resolve, reject) => {
                try {
                    const tableBody = document.getElementById("partitionTableBody");
                    const partitions = disks[selectedDisk].children;

                    tableBody.innerHTML = "";

                    if (partitions) {
                        partitions.forEach(partition => {
                            const row = tableBody.insertRow();

                            const partNoCell = row.insertCell();
                            partNoCell.textContent = partition.partn;
                            partNoCell.setAttribute("scope", "row");
                            partNoCell.classList.add("col-1");

                            const labelCell = row.insertCell();
                            if (partition.label != null) {
                                labelCell.textContent = partition.label;
                            }
                            else {
                                labelCell.textContent = partition.name;
                            }
                            labelCell.classList.add("col-2");

                            const typeCell = row.insertCell();
                            if (partition.parttypename != null) {
                                typeCell.textContent = partition.parttypename;
                            }
                            else {
                                typeCell.textContent = "Unknown";
                            }
                            typeCell.classList.add("col-2");

                            const sizeCell = row.insertCell();
                            sizeCell.textContent = partition.size;
                            sizeCell.classList.add("col-1");

                            const contentsCell = row.insertCell();
                            if (partition.fstype != null) {
                                contentsCell.textContent = `${partition.fstype} (Ver. ${partition.fsver})`;
                            }
                            else {
                                contentsCell.textContent = "Unknown";
                            }
                            contentsCell.classList.add("col-3");

                            const UUIDCell = row.insertCell();
                            if (partition.uuid != null) {
                                UUIDCell.textContent = partition.uuid;
                            }
                            else {
                                UUIDCell.textContent = "Unknown";
                            }
                            UUIDCell.classList.add("col-3");
                        });
                    }

                    resolve();
                } catch (error) {
                    console.error("Error updating partition table:", error);
                    reject(error);
                }
            });
        }
    });

})(jQuery);
