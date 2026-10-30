/**
 * theme.js
 * Instant dark/light theme switching with no page reload, persisted to
 * localStorage. Applied as early as possible (inline in <head>) to avoid a
 * flash of the wrong theme; this file only wires up the toggle control.
 */
(function () {
  const STORAGE_KEY = "smart-retry-theme";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }

  function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY) || "dark";
    document.documentElement.setAttribute("data-theme", saved);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    applyTheme(current === "dark" ? "light" : "dark");
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    const toggle = document.getElementById("themeToggle");
    if (toggle) {
      toggle.addEventListener("click", toggleTheme);
    }
  });

  // Expose for command palette / keyboard shortcut use
  window.SmartRetryTheme = { toggle: toggleTheme, apply: applyTheme };
})();
