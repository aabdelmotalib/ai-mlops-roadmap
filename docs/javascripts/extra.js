/* ============================================================
   extra.js — Custom JavaScript for The AI & MLOps Engineer Roadmap
   ============================================================ */

// Initialize Mermaid diagrams with current theme
document$.subscribe(function () {
  const isDark = document.body.getAttribute("data-md-color-scheme") === "slate";
  mermaid.initialize({
    startOnLoad: true,
    theme: isDark ? "dark" : "default",
  });
});
