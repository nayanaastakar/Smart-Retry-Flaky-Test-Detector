/**
 * dashboard_charts.js
 * Renders the Chart.js visuals on the dashboard using colors pulled from the
 * active CSS theme so charts stay correct across dark/light switches.
 */
function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function initDashboardCharts(data) {
  const gridColor = cssVar("--border-subtle");
  const textColor = cssVar("--text-secondary");
  const fontFamily = "Inter, sans-serif";

  Chart.defaults.color = textColor;
  Chart.defaults.font.family = fontFamily;
  Chart.defaults.font.size = 11;

  // ---- Execution trend (line) ----
  const trendCtx = document.getElementById("trendChart");
  if (trendCtx) {
    new Chart(trendCtx, {
      type: "line",
      data: {
        labels: data.trend.labels.map((d) => d.slice(5)),
        datasets: [
          { label: "Pass", data: data.trend.pass, borderColor: cssVar("--status-pass"), backgroundColor: "transparent", tension: 0.35, pointRadius: 0, borderWidth: 2 },
          { label: "Fail", data: data.trend.fail, borderColor: cssVar("--status-fail"), backgroundColor: "transparent", tension: 0.35, pointRadius: 0, borderWidth: 2 },
          { label: "Flaky", data: data.trend.flaky, borderColor: cssVar("--status-flaky"), backgroundColor: "transparent", tension: 0.35, pointRadius: 0, borderWidth: 2 },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "top", align: "end", labels: { boxWidth: 8, boxHeight: 8, usePointStyle: true } } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: gridColor }, beginAtZero: true, ticks: { precision: 0 } },
        },
      },
    });
  }

  // ---- Status distribution (doughnut) ----
  const pieCtx = document.getElementById("statusPie");
  if (pieCtx) {
    new Chart(pieCtx, {
      type: "doughnut",
      data: {
        labels: ["Pass", "Fail", "Flaky", "Skipped"],
        datasets: [{
          data: [data.statusDist.PASS, data.statusDist.FAIL, data.statusDist.FLAKY, data.statusDist.SKIPPED],
          backgroundColor: [cssVar("--status-pass"), cssVar("--status-fail"), cssVar("--status-flaky"), cssVar("--text-tertiary")],
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        cutout: "68%",
        plugins: { legend: { position: "bottom", labels: { boxWidth: 8, boxHeight: 8, usePointStyle: true, padding: 16 } } },
      },
    });
  }

  // ---- Retry trend (bar) ----
  const retryCtx = document.getElementById("retryChart");
  if (retryCtx) {
    new Chart(retryCtx, {
      type: "bar",
      data: {
        labels: data.retryTrend.labels.map((d) => d.slice(5)),
        datasets: [{ label: "Avg Attempts", data: data.retryTrend.values, backgroundColor: cssVar("--accent"), borderRadius: 4, maxBarThickness: 22 }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: gridColor }, beginAtZero: true },
        },
      },
    });
  }
}
