(function($) {
    'use strict';
    $(function() {
        let gpuDetails;
        let gpuMetrics;
        let selectedGPUIndex = 0;
        const dropDownMenuButton = document.getElementById("dropDownButtonText");

        let gpuTempChart;
        let gpuTempLabels = Array(60).fill("");
        let gpuTempData = Array(60).fill(0);
        let gpuTempText = document.getElementById("gpuTempText");

        let gpuUtilChart;
        let gpuUtilLabels = Array(60).fill("");
        let gpuUtilDatasets = [];
        let gpuUtilText = document.getElementById("gpuUtilText")

        var graphGradient = document.getElementById("gpuTempChart").getContext('2d');
        var graphGradient2 = document.getElementById("gpuTempChart").getContext('2d');
        var saleGradientBg = graphGradient.createLinearGradient(5, 0, 5, 100);
        saleGradientBg.addColorStop(0, 'rgba(26, 115, 232, 0.18)');
        saleGradientBg.addColorStop(1, 'rgba(26, 115, 232, 0.02)');
        var saleGradientBg2 = graphGradient2.createLinearGradient(100, 0, 50, 150);
        saleGradientBg2.addColorStop(0, 'rgba(0, 208, 255, 0.19)');
        saleGradientBg2.addColorStop(1, 'rgba(0, 208, 255, 0.03)');

        if ($("#gpuUtilizationChart").length) {
            const ctx = document.getElementById('gpuUtilizationChart');

            gpuUtilChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: gpuUtilLabels,
                    datasets: gpuUtilDatasets
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
                            max: 100,
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
                                text: "Utilization (%)",
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
                            callbacks: {
                                label: function(tooltipItem) {
                                    return tooltipItem.dataset.label + ': ' + tooltipItem.raw.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        }

        if ($("#gpuTempChart").length) {
            const ctx = document.getElementById('gpuTempChart');

            gpuTempChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: gpuTempLabels,
                    datasets: [
                        {
                            data: gpuTempData,
                            backgroundColor: gpuTempData.map(temp => {
                                if (temp <= 85) {
                                    return '#90EE90';
                                } else if (temp <= 90) {
                                    return 'orange';
                                } else {
                                    return 'red';
                                }
                            }),
                            borderWidth: 1,
                            barPercentage: 0.8,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            ticks: {
                                display: false,
                            },
                            title: {
                                display: false,
                            },
                            grid: {
                                display: false,
                            }
                        },
                        y: {
                            beginAtZero: false,
                            suggestedMin: 30,
                            suggestedMax: 100,
                            title: {
                                display: true,
                                text: "Temperature (°C)",
                            },
                        },
                    },
                    animation: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                },
            });
        }


        const socket = new WebSocket('ws://' + window.location.host + '/ws/gpu/');

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
                if (data.details) {
                    gpuDetails = data.details;
                    await updateGPUDetailsAsync();
                    await updateGPUChoiceDropdownItemsAsync();
                }

                if (data.metrics) {
                    gpuMetrics = data.metrics
                    await updateGPUUtilChartAsync();
                    await updateGPUTempChartAsync();
                    await updateGPUAdditionalStats();
                }
            }
        };

        async function updateGPUUtilChartAsync() {
            return new Promise((resolve, reject) => {
                try {
                    let gpu = gpuMetrics[selectedGPUIndex];
                    let now = new Date().toLocaleTimeString();

                    if (gpu) {
                        let gpuUtil = parseFloat(gpu.gpu_utilization);

                        if (!gpuUtilDatasets.length) {
                            gpuUtilDatasets.push({
                                label: "GPU Utilization",
                                data: Array(60).fill(0),
                                backgroundColor: "rgba(75,192,192,0.4)",
                                borderColor: "rgba(75,192,192,1)",
                                borderWidth: 1,
                                pointRadius: 0,
                            });
                        }

                        if (gpuUtilLabels.length >= 60) {
                            gpuUtilLabels.shift();
                            gpuUtilDatasets[0].data.shift();
                        }

                        gpuUtilLabels.push(now);
                        gpuUtilDatasets[0].data.push(gpuUtil);

                        gpuUtilChart.data.labels = gpuUtilLabels;
                        gpuUtilChart.data.datasets[0].data = gpuUtilDatasets[0].data;

                        gpuUtilChart.update();

                        gpuUtilText.innerText = `${gpuUtil} %`;
                    }
                    resolve();
                } catch (error) {
                    console.error("Error updating GPU utilization chart:", error);
                    reject(error);
                }
            });
        }

        async function updateGPUTempChartAsync() {
            return new Promise((resolve, reject) => {
                try {
                    let gpuTemp = gpuMetrics[selectedGPUIndex].temperature;
                    let now = new Date().toLocaleTimeString();

                    if (gpuTempLabels.length >= 60) {
                        gpuTempLabels.shift();
                        gpuTempData.shift();
                    }

                    gpuTempLabels.push(now);
                    gpuTempData.push(gpuTemp);

                    gpuTempChart.update();

                    gpuTempText.innerHTML = `${gpuTemp}°C`

                    resolve();
                } catch (error) {
                    console.log("Error updating GPU temperature chart:", error);
                    reject(error);
                }
            });
        }

        async function updateGPUAdditionalStats() {
            return new Promise((resolve, reject) => {
                try {
                    let memUsed = gpuMetrics[selectedGPUIndex].memory_used;
                    let memUtil = gpuMetrics[selectedGPUIndex].memory_utilization;
                    let memTotal = gpuDetails[selectedGPUIndex].total_vram;
                    let powerDraw = gpuMetrics[selectedGPUIndex].power_draw;
                    let powerMax = gpuDetails[selectedGPUIndex].max_power;

                    const memUsedText = document.getElementById("memUsed");
                    const memUtilProgressBar = document.getElementById("memUtilProgressBar");
                    const powerDrawText = document.getElementById("powerDraw");
                    const powerDrawProgressBar = document.getElementById("powerDrawProgressBar");

                    memUsedText.innerText = `${memUsed} / ${memTotal} MiB`;
                    memUtilProgressBar.setAttribute("aria-valuenow", memUtil);
                    memUtilProgressBar.setAttribute("style", `width: ${memUtil}%`);

                    let powerDrawFloat = parseFloat(powerDraw);
                    let powerMaxFloat = parseFloat(powerMax);
                    let powerUtil = powerDrawFloat / powerMaxFloat * 100;
                    powerDrawText.innerText = `${powerDraw} / ${powerMax} W`;
                    powerDrawProgressBar.setAttribute("aria-valuenow", powerUtil);
                    powerDrawProgressBar.setAttribute("style", `width: ${powerUtil}%`);

                    resolve();
                } catch (error) {
                    console.log("Error updating GPU additional stats:", error);
                    reject(error);
                }
            });
        }

        async function updateGPUDetailsAsync() {
            return new Promise((resolve, reject) => {
                try {
                    document.getElementById("vendor").innerText = gpuDetails[selectedGPUIndex].vendor;
                    document.getElementById("model").innerText = gpuDetails[selectedGPUIndex].model;
                    document.getElementById("uuid").innerText = gpuDetails[selectedGPUIndex].uuid;
                    document.getElementById("driverVersion").innerText = gpuDetails[selectedGPUIndex].driver_version;
                    document.getElementById("vram").innerText = `${gpuDetails[selectedGPUIndex].total_vram} MiB`;
                    document.getElementById("minPower").innerText = `${gpuDetails[selectedGPUIndex].min_power} W`;
                    document.getElementById("maxPower").innerText = `${gpuDetails[selectedGPUIndex].max_power} W`;

                    resolve();
                } catch (error) {
                    console.error("Error updating GPU details:", error);
                    reject(error);
                }
            });
        }

        async function updateGPUChoiceDropdownItemsAsync() {
            return new Promise((resolve, reject) => {
                try {
                    const dropdownMenu = document.querySelector('.dropdown-menu');
                    dropdownMenu.innerHTML = '';

                    Object.keys(gpuDetails).forEach(index => {
                        let gpu = gpuDetails[index];
                        const newItem = document.createElement('a');
                        newItem.classList.add('dropdown-item');
                        newItem.href = '#';
                        newItem.textContent = `GPU ${gpu.index}: ${gpu.model}`;
                        newItem.setAttribute("data-index", index);
                        dropdownMenu.appendChild(newItem);

                        newItem.addEventListener('click', (event) => {
                            const index = event.target.getAttribute('data-index');

                            selectedGPUIndex = index;
                            dropDownMenuButton.innerText = `GPU ${gpu.index}: ${gpu.model}`;
                            diskUtilDatasets = Array(60).fill(0.00);
                            diskUtilLabels = Array(60).fill("");
                        });
                    });

                    dropDownMenuButton.innerText = `GPU ${gpuDetails[selectedGPUIndex].index}: ${gpuDetails[selectedGPUIndex].model}`;

                    resolve();
                } catch (error) {
                    console.error("Error updating dropdown content:", error);
                    reject(error);
                }
            });
        }
    });
})(jQuery);
