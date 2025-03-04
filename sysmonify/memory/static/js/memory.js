(function($) {
    'use strict';
    $(function() {
        let memoryChart;
        const memoryCanvas = document.getElementById('memoryChart');
        let memoryDatasets = [{
            data: [0, 0],
            backgroundColor: [
                "#e8e8e8",
                "#40e0d0",
            ],
            borderColor: [
                "#e8e8e8",
                "#40e0d0",
            ],
        }];
        let memoryData;
        const memoryUtilText = document.getElementById("memoryUtilText");

        let swapChart;
        const swapCanvas = document.getElementById('swapChart');
        let swapDatasets = [{
            data: [0, 0],
            backgroundColor: [
                "#e8e8e8",
                "#40e0d0",
            ],
            borderColor: [
                "#e8e8e8",
                "#40e0d0",
            ],
        }];
        let swapData;
        const swapChartText = document.getElementById("swapUtilText");

        if ($("#memoryChart").length) {
            memoryChart = new Chart(memoryCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Free','Used'],
                    datasets: memoryDatasets
                },
                options: {
                    cutout: 120,
                    animationEasing: "easeOutBounce",
                    animateRotate: true,
                    animateScale: false,
                    responsive: true,
                    maintainAspectRatio: true,
                    showScale: true,
                    legend: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            align: 'center',
                            labels: {
                                color: '#333',
                                font: {
                                    size: 14,
                                    family: 'Arial',
                                    weight: 'bold'
                                },
                                marginTop: 40,
                                padding: 20,
                                boxWidth: 20,
                                boxHeight: 20,
                                usePointStyle: true,
                            },
                        },
                        layout: {
                            padding: {
                                bottom: 60,
                            },
                        }
                    }
                },
                plugins: [{}]
            });
        }

        if ($("#swapChart").length) {
            swapChart = new Chart(swapCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Free','Used'],
                    datasets: swapDatasets
                },
                options: {
                    cutout: 120,
                    animationEasing: "easeOutBounce",
                    animateRotate: true,
                    animateScale: false,
                    responsive: true,
                    maintainAspectRatio: true,
                    showScale: true,
                    legend: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            align: 'center',
                            labels: {
                                color: '#333',
                                font: {
                                    size: 14,
                                    family: 'Arial',
                                    weight: 'bold'
                                },
                                marginTop: 40,
                                padding: 20,
                                boxWidth: 20,
                                boxHeight: 20,
                                usePointStyle: true,
                            },
                        },
                        layout: {
                            padding: {
                                bottom: 60,
                            },
                        },
                    }
                },
                plugins: [{}]
            });
        }

        const socket = new WebSocket('ws://' + window.location.host + '/ws/memory/');

        socket.onopen = function(e) {
            console.log("Successfully connected to WebSocket.");
        };

        socket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly.');
        };

        socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            if (data){
                if (data.metrics) {
                    console.log(data.metrics);
                    if (data.metrics.memory) {
                        memoryData = data.metrics.memory;
                        await updateMemoryChartAsync();
                    }
                    if (data.metrics.swap) {
                        swapData = data.metrics.swap;
                        await updateSwapChartAsync();
                    }
                }
            }
        };

        async function updateMemoryChartAsync() {
            new Promise((resolve, reject) => {
                try {
                    memoryDatasets[0].data[1] = memoryData.used / 1024 / 1024;
                    memoryDatasets[0].data[0] = memoryData.free / 1024 / 1024;

                    memoryChart.update();

                    const memUtilization = (memoryData.used / memoryData.total * 100).toFixed(1);
                    memoryUtilText.textContent = `Utilization: ${memUtilization}%`;

                    resolve();
                } catch (error) {
                    console.error("Error while updating memory chart. ", error);
                    reject();
                }
            });
        }

        async function updateSwapChartAsync() {
            new Promise((resolve, reject) => {
                try {
                    swapDatasets[0].data[1] = swapData.used / 1024 / 1024;
                    swapDatasets[0].data[0] = swapData.free / 1024 / 1024;

                    swapChart.update();

                    const swapUtilization = (swapData.used / swapData.total * 100).toFixed(1);
                    swapUtilText.textContent = `Utilization: ${swapUtilization}%`;

                    resolve();
                } catch (error) {
                    console.error("Error while updating swap chart. ", error);
                    reject();
                }
            });
        }
    });

})(jQuery);
