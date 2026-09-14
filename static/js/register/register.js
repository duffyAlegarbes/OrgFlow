document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registerForm");
    const registerBtn = document.getElementById("registerBtn");

    if (registerForm && registerBtn) {
        registerForm.addEventListener("submit", function () {
            registerBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating Account...';
        });
    }
});