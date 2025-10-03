document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[type='password']").forEach((input) => {
    input.classList.add("input-password");

    const togglePasswordButton = document.createElement("button");
    togglePasswordButton.type = "button";
    togglePasswordButton.classList.add("toggle-password");
    // Append button to input group
    input.parentElement.appendChild(togglePasswordButton);

    togglePasswordButton.addEventListener("click", () => {
      if (input.type === "password") {
        input.type = "text";
      } else {
        input.type = "password";
      }
    });
  });
});
