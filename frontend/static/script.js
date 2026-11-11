/**
 * ApnaGhar — Professional House Broker UI Script
 * Strict Non-AI, Clean Architectural Pair Programming JS
 * Handles Quick Admin Demo Login, Password Visibility Toggle, and Form Polish.
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Quick Admin Demo Login Handler
  const quickLoginBtn = document.getElementById("quick-login-btn");
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const loginForm = document.getElementById("login-form");

  if (quickLoginBtn && usernameInput && passwordInput && loginForm) {
    quickLoginBtn.addEventListener("click", function (event) {
      event.preventDefault();

      const adminId = quickLoginBtn.getAttribute("data-id") || "Admin";
      const adminPass = quickLoginBtn.getAttribute("data-pass") || "Admin@1234";

      // Populate input values
      usernameInput.value = adminId;
      passwordInput.value = adminPass;

      // Subtle solid architectural highlight
      usernameInput.style.borderColor = "#9c783e";
      usernameInput.style.backgroundColor = "#fbf7f0";
      passwordInput.style.borderColor = "#9c783e";
      passwordInput.style.backgroundColor = "#fbf7f0";

      // Update button text for immediate feedback
      const originalText = quickLoginBtn.innerHTML;
      quickLoginBtn.innerHTML = "Authenticating Admin...";
      quickLoginBtn.style.opacity = "0.9";

      // Smooth submission
      setTimeout(function () {
        loginForm.submit();
      }, 160);
    });
  }

  // 2. Toggle Password Visibility
  const togglePassBtn = document.getElementById("toggle-password-btn");
  if (togglePassBtn && passwordInput) {
    togglePassBtn.addEventListener("click", function () {
      const currentType = passwordInput.getAttribute("type");
      if (currentType === "password") {
        passwordInput.setAttribute("type", "text");
        togglePassBtn.textContent = "Hide";
      } else {
        passwordInput.setAttribute("type", "password");
        togglePassBtn.textContent = "Show";
      }
    });
  }

  // 3. Smooth Select & Input Focus Effects
  const formControls = document.querySelectorAll(".form-input, .form-field input, .form-field select");
  formControls.forEach(function (control) {
    control.addEventListener("focus", function () {
      const parent = control.closest(".form-field") || control.closest(".form-group");
      if (parent) {
        parent.classList.add("field-focused");
      }
    });

    control.addEventListener("blur", function () {
      const parent = control.closest(".form-field") || control.closest(".form-group");
      if (parent) {
        parent.classList.remove("field-focused");
      }
    });
  });
});
