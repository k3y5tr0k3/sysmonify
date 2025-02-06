(function($) {
    'use strict';
    $(function() {
        let cpuTempChart;
        let cpuTempLabels = Array(60).fill("");
        let cpuTempData = Array(60).fill(0);
        let cpuTempText = document.getElementById("cpuPackageTempText");

        let cpuUtilChart;
        let cpuUtilLabels = Array(15).fill("");
        let cpuUtilDatasets = [];
        let cpuCoreCount = 0;
        let cpuMinFreq = 400;
        let cpuMaxFreq = 5000;
        let cpuAvgFreqText = document.getElementById("cpuAvgFreqText")

        var graphGradient = document.getElementById("cpuTempChart").getContext('2d');
        var graphGradient2 = document.getElementById("cpuTempChart").getContext('2d');
        var saleGradientBg = graphGradient.createLinearGradient(5, 0, 5, 100);
        saleGradientBg.addColorStop(0, 'rgba(26, 115, 232, 0.18)');
        saleGradientBg.addColorStop(1, 'rgba(26, 115, 232, 0.02)');
        var saleGradientBg2 = graphGradient2.createLinearGradient(100, 0, 50, 150);
        saleGradientBg2.addColorStop(0, 'rgba(0, 208, 255, 0.19)');
        saleGradientBg2.addColorStop(1, 'rgba(0, 208, 255, 0.03)');

        if ($("#cpuUtilizationChart").length) {
            const ctx = document.getElementById('cpuUtilizationChart');

            cpuUtilChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: cpuUtilLabels,
                    datasets: cpuUtilDatasets
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
                            min: cpuMinFreq,
                            max: cpuMaxFreq,
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
                                text: "Frequency (Mhz)",
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

        if ($("#cpuTempChart").length) {
            const ctx = document.getElementById('cpuTempChart');

            cpuTempChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: cpuTempLabels,
                    datasets: [
                        {
                            data: cpuTempData,
                            backgroundColor: cpuTempData.map(temp => {
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

        const socket = new WebSocket('ws://' + window.location.host + '/ws/cpu/');

        socket.onopen = function(e) {
            console.log("Successfully connected to WebSocket.");
        };

        socket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly.');
        };

        socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            if (data){
                if (data.details) {
                    await updateCPUDetailsAsync(data.details);
                }

                if (data.temp) {
                    const tempValue = parseFloat(data.temp.package);
                    if (!isNaN(tempValue)) {
                        await updateTempChartAsync(tempValue);
                    } else {
                        console.error("Received invalid CPU temperature value:", data.temp.package);
                    }
                }

                if (data.freq) {
                    await updateUtilChartAsync(data.freq);
                }
            }

        };

        async function updateTempChartAsync(data) {
            return new Promise((resolve, reject) => {
                try {
                    cpuTempData.push(data);
                    cpuTempLabels.push(new Date().toLocaleTimeString());

                    if (cpuTempData.length > 60) {
                        cpuTempData.shift();
                        cpuTempLabels.shift();
                    }

                    cpuTempChart.update();

                    cpuTempText.innerText = `${data}°C`;

                    resolve();
                } catch (error) {
                    reject(error);
                }
            });
        }

        async function updateUtilChartAsync(data) {
            return new Promise((resolve, reject) => {
                try {
                    let newLabels = [...cpuUtilLabels];
                    newLabels.push(new Date().toLocaleTimeString());
                    if (newLabels.length > 15) newLabels.shift();

                    cpuCoreCount = Object.keys(data).length
                    let totalCoreFreq = 0.0;

                    Object.keys(data).forEach((coreId, index) => {
                        let freqValue = parseFloat(data[coreId]);
                        if (isNaN(freqValue)) {
                            console.warn(`Invalid frequency data for ${coreId}:`, data[coreId]);
                            return;
                        }

                        let uniqueColor = generateColor(index);
                        let dataset = cpuUtilDatasets.find(ds => ds.label === coreId);

                        if (!dataset) {
                            dataset = {
                                label: coreId,
                                data: Array(15).fill(0),
                                backgroundColor: uniqueColor.replace("hsl", "hsla").replace(")", ", 0.3)"),
                                borderColor: uniqueColor,
                                borderWidth: 1.5,
                                fill: false,
                                pointBorderWidth: 1,
                                pointRadius: 3,
                                pointBackgroundColor: uniqueColor,
                                pointBorderColor: '#fff',
                            };
                            cpuUtilDatasets.push(dataset);
                        }

                        dataset.data.push(freqValue);
                        if (dataset.data.length > 15) dataset.data.shift();

                        totalCoreFreq += freqValue;
                    });

                    cpuUtilChart.data.labels = newLabels;
                    cpuUtilChart.data.datasets = cpuUtilDatasets;
                    cpuUtilChart.update();

                    let averageCoreFreq = totalCoreFreq / cpuCoreCount;
                    cpuAvgFreqText.innerText = `Avg. ${averageCoreFreq.toFixed(2)} Mhz`

                    resolve();
                } catch (error) {
                    console.error("Error updating utilization chart:", error);
                    reject(error);
                }
            });
        }

        async function updateCPUDetailsAsync(data) {
            return new Promise((resolve, reject) => {
                try {
                    document.getElementById("vendor").innerText = data.vendor;
                    document.getElementById("model").innerText = data.model;
                    document.getElementById("architecture").innerText = data.architecture;
                    document.getElementById("socket").innerText = data.socket;
                    document.getElementById("cores").innerText = data.cores;
                    document.getElementById("threads").innerText = data.threads;
                    document.getElementById("maxTurbo").innerText = data.turbo_frequency;
                    document.getElementById("l1Cache").innerText = data.cache_sizes.l1;
                    document.getElementById("l2Cache").innerText = data.cache_sizes.l2;
                    document.getElementById("l3Cache").innerText = data.cache_sizes.l3;

                    resolve();
                } catch (error) {
                    console.error("Error updating utilization chart:", error);
                    reject(error);
                }
            });
        }

        const generateColor = (index) => {
            const hueStep = 360 / (cpuCoreCount / 2);
            const hue = (index * hueStep) % 360;

            const saturation = 60 + (index % 2) * 20;
            const lightness = 40 + (index % 2) * 30;

            return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
        }
    });

})(jQuery);
