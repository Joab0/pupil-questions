document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("sidebar-toggle");

  toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");

    // Change toggle icon
    const icon = toggleBtn.querySelector("i");
    if (sidebar.classList.contains("collapsed")) {
      icon.className = "bi bi-text-indent-left"; // expand icon
    } else {
      icon.className = "bi bi-text-indent-right"; // collapse icon
    }

    // Save state
    localStorage.setItem(
      "sidebar-collapsed",
      sidebar.classList.contains("collapsed")
    );
  });

  // Get state
  if (localStorage.getItem("sidebar-collapsed") === "true") {
    sidebar.classList.add("collapsed");
  }
});
