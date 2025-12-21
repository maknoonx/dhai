// Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initSalesChart();
});

/**
 * Initialize sales chart
 */
function initSalesChart() {
    const canvas = document.getElementById('salesChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Sales data by hour
    const data = {
        labels: [
            '12 صباحاً', '1 صباحاً', '2 صباحاً', '3 صباحاً', '4 صباحاً', '5 صباحاً',
            '6 صباحاً', '7 صباحاً', '8 صباحاً', '9 صباحاً', '10 صباحاً', '11 صباحاً',
            '12 ظهراً', '1 مساءً', '2 مساءً', '3 مساءً', '4 مساءً', '5 مساءً',
            '6 مساءً', '7 مساءً', '8 مساءً', '9 مساءً', '10 مساءً', '11 مساءً'
        ],
        datasets: [{
            label: 'المبيعات (ريال)',
            data: [
                0, 0, 0, 0, 0, 0, 0, 0,
                450, 1200, 1850, 2100, 1950, 1400,
                900, 1100, 1650, 2200, 2450, 2100,
                1800, 1200, 650, 200
            ],
            borderColor: '#4A9EAD',
            backgroundColor: createGradient(ctx),
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: '#4A9EAD',
            pointHoverBorderColor: '#fff',
            pointHoverBorderWidth: 2
        }]
    };
    
    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'white',
                    titleColor: '#2d3748',
                    bodyColor: '#2d3748',
                    borderColor: '#e2e8f0',
                    borderWidth: 1,
                    padding: 12,
                    boxPadding: 6,
                    usePointStyle: true,
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toLocaleString('ar-SA') + ' ريال';
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: true,
                        color: '#f0f0f0',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: 'Cairo',
                            size: 12
                        },
                        color: '#9ca3af',
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    grid: {
                        display: true,
                        color: '#f0f0f0',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: 'Cairo',
                            size: 12
                        },
                        color: '#9ca3af',
                        callback: function(value) {
                            return value.toLocaleString('ar-SA');
                        }
                    },
                    beginAtZero: true
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };
    
    new Chart(ctx, config);
}

/**
 * Create gradient for chart
 */
function createGradient(ctx) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 320);
    gradient.addColorStop(0, 'rgba(74, 158, 173, 0.3)');
    gradient.addColorStop(1, 'rgba(74, 158, 173, 0)');
    return gradient;
}

/**
 * Update chart with new data (for future AJAX updates)
 */
function updateSalesChart(newData) {
    const chart = Chart.getChart('salesChart');
    if (chart) {
        chart.data.datasets[0].data = newData;
        chart.update();
    }
}

/**
 * Refresh dashboard stats (for future implementation)
 */
function refreshDashboardStats() {
    // This will be implemented later with AJAX
    console.log('Refreshing dashboard stats...');
}

// Auto-refresh every 5 minutes (optional)
// setInterval(refreshDashboardStats, 300000);
