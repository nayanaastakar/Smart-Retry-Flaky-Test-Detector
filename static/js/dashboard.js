/* 
  dashboard.js - Module 7
  Handles dynamic charts and History actions
*/

function deleteExecution(executionId) {
    if (!confirm('Are you sure you want to delete this execution history?')) return;
    
    $.ajax({
        url: '/api/history/' + executionId,
        type: 'DELETE',
        success: function(res) {
            const toast = $('<div class="alert alert-success alert-dismissible position-fixed top-0 end-0 m-3" style="z-index:9999">Execution deleted.<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>');
            $('body').append(toast);
            setTimeout(function() { location.reload(); }, 1200);
        },
        error: function(err) {
            alert('Failed to delete execution.');
            console.error(err);
        }
    });
}

function renderCharts(chartData) {
    if (!chartData) return;

    // ── 1. Doughnut Chart (Pass vs Fail vs Flaky) ────────────────────────────
    const pieCtx = document.getElementById('resultsPieChart');
    if (pieCtx) {
        const passed = chartData.pie.passed || 0;
        const failed = chartData.pie.failed || 0;
        const flaky  = chartData.pie.flaky  || 0;
        const total  = passed + failed + flaky;

        new Chart(pieCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Passed', 'Failed', 'Flaky'],
                datasets: [{
                    data: total > 0 ? [passed, failed, flaky] : [1, 0, 0],
                    backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                    borderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '68%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#e2e8f0',
                            padding: 12,
                            boxWidth: 12,
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) { return ' ' + ctx.label + ': ' + ctx.parsed; }
                        }
                    }
                }
            }
        });
    }

    // ── 2. Stacked Bar Chart (Execution Trend) ───────────────────────────────
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        const labels  = chartData.trend.labels  || [];
        const passed  = chartData.trend.passed  || [];
        const failed  = chartData.trend.failed  || [];
        const flaky   = chartData.trend.flaky   || [];

        // Compute max Y so bars don't fill entire canvas
        const maxY = Math.max.apply(null, labels.map(function(_, i) {
            return (passed[i] || 0) + (failed[i] || 0) + (flaky[i] || 0);
        }).concat([5])) + 1;

        new Chart(trendCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Passed', data: passed, backgroundColor: '#10b981', maxBarThickness: 32, borderRadius: 4 },
                    { label: 'Failed', data: failed, backgroundColor: '#ef4444', maxBarThickness: 32, borderRadius: 4 },
                    { label: 'Flaky',  data: flaky,  backgroundColor: '#f59e0b', maxBarThickness: 32, borderRadius: 4 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        ticks: { color: '#94a3b8', maxRotation: 0, font: { size: 11 } },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        max: maxY,
                        ticks: { color: '#94a3b8', stepSize: 1, precision: 0 },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#e2e8f0', padding: 16, boxWidth: 12, font: { size: 12 } }
                    }
                },
                animation: { duration: 500 }
            }
        });
    }
}
