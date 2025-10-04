const html = document.documentElement;
const icon = document.getElementById("theme-icon");
const toggle = document.getElementById("theme-toggle");

// Bootstrap icons
const icons = {
  light: "bi-moon-fill",
  dark: "bi-sun-fill",
};

function applyTheme(theme) {
  html.setAttribute("data-bs-theme", theme);
  icon.className = `bi ${icons[theme]}`;
  localStorage.setItem("theme", theme);
}

window.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "light";
  applyTheme(savedTheme);
});

toggle.addEventListener("click", () => {
  const currentTheme = html.getAttribute("data-bs-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";
  applyTheme(newTheme);
});
