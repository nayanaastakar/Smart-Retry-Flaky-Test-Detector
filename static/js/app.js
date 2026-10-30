/**
 * app.js
 * Shared front-end behaviors: toast notifications, command palette (Ctrl/Cmd+K),
 * keyboard shortcuts, and dashboard auto-refresh.
 */

// ---------------------------------------------------------------------------
// Toast notifications
// ---------------------------------------------------------------------------
function showToast(message, type = "info", duration = 4000) {
  let stack = document.querySelector(".toast-stack");
  if (!stack) {
    stack = document.createElement("div");
    stack.className = "toast-stack";
    document.body.appendChild(stack);
  }
  const icons = { success: "fa-circle-check", error: "fa-circle-exclamation", info: "fa-circle-info" };
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i><span>${message}</span>`;
  stack.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.25s ease";
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-flash]").forEach((el) => {
    showToast(el.dataset.flash, el.dataset.flashType || "info");
  });
});

// ---------------------------------------------------------------------------
// Command palette (Ctrl/Cmd + K)
// ---------------------------------------------------------------------------
const COMMANDS = [
  { label: "Go to Dashboard", icon: "fa-gauge-high", href: "/" },
  { label: "Go to Execution History", icon: "fa-clock-rotate-left", href: "/history/" },
  { label: "Go to Settings", icon: "fa-sliders", href: "/settings/" },
  { label: "Go to Profile", icon: "fa-user", href: "/profile/" },
  { label: "Toggle Theme", icon: "fa-circle-half-stroke", action: () => window.SmartRetryTheme.toggle() },
  { label: "Export History (CSV)", icon: "fa-file-csv", href: "/history/export.csv" },
];

function buildPalette() {
  const overlay = document.createElement("div");
  overlay.id = "cmdPaletteOverlay";
  overlay.style.cssText = `position:fixed;inset:0;background:rgba(4,7,15,0.55);backdrop-filter:blur(3px);
    display:flex;align-items:flex-start;justify-content:center;padding-top:12vh;z-index:1000;`;
  overlay.innerHTML = `
    <div style="width:560px;max-width:92vw;background:var(--bg-surface-raised);border:1px solid var(--border-strong);
      border-radius:14px;box-shadow:var(--shadow-pop);overflow:hidden;">
      <input id="cmdInput" placeholder="Type a command or search..." autocomplete="off"
        style="width:100%;box-sizing:border-box;padding:16px 18px;background:transparent;border:none;
        border-bottom:1px solid var(--border-subtle);color:var(--text-primary);font-size:14px;outline:none;font-family:var(--font-ui);" />
      <div id="cmdList" style="max-height:320px;overflow-y:auto;padding:8px;"></div>
    </div>`;
  document.body.appendChild(overlay);

  const list = overlay.querySelector("#cmdList");
  const input = overlay.querySelector("#cmdInput");

  function render(filter = "") {
    list.innerHTML = "";
    COMMANDS.filter((c) => c.label.toLowerCase().includes(filter.toLowerCase())).forEach((c) => {
      const item = document.createElement("div");
      item.style.cssText = `display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:8px;
        cursor:pointer;font-size:13.5px;color:var(--text-primary);`;
      item.innerHTML = `<i class="fa-solid ${c.icon}" style="width:16px;color:var(--accent-hover);"></i>${c.label}`;
      item.onmouseenter = () => (item.style.background = "var(--bg-surface-hover)");
      item.onmouseleave = () => (item.style.background = "transparent");
      item.onclick = () => {
        overlay.remove();
        if (c.href) window.location.href = c.href;
        if (c.action) c.action();
      };
      list.appendChild(item);
    });
  }

  render();
  input.addEventListener("input", (e) => render(e.target.value));
  input.focus();
  overlay.addEventListener("click", (e) => { if (e.target === overlay) overlay.remove(); });
  document.addEventListener("keydown", function esc(e) {
    if (e.key === "Escape") { overlay.remove(); document.removeEventListener("keydown", esc); }
  });
}

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    if (!document.getElementById("cmdPaletteOverlay")) buildPalette();
  }
});

// ---------------------------------------------------------------------------
// Dashboard auto-refresh (soft reload of KPI values via API, no full page reload)
// ---------------------------------------------------------------------------
function initAutoRefresh(intervalMs = 30000) {
  if (!document.body.classList.contains("page-dashboard")) return;
  setInterval(async () => {
    try {
      const res = await fetch("/api/v1/analytics/summary");
      if (!res.ok) return;
      const data = await res.json();
      const map = {
        total_executions: "kpiTotal",
        passed: "kpiPassed",
        failed: "kpiFailed",
        flaky: "kpiFlaky",
      };
      Object.entries(map).forEach(([key, id]) => {
        const el = document.getElementById(id);
        if (el && data[key] !== undefined) el.textContent = data[key];
      });
    } catch (err) {
      // silent - auto refresh should never disrupt the UI
    }
  }, intervalMs);
}
document.addEventListener("DOMContentLoaded", () => initAutoRefresh());
