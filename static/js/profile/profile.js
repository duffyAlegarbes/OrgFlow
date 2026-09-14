document.addEventListener("DOMContentLoaded", function () {
    // 1. Avatar click & auto-submit
    const avatarContainer = document.getElementById("avatarContainer");
    const profileImageInput = document.getElementById("profileImageInput");
    const avatarForm = document.getElementById("avatarForm");

    if (avatarContainer && profileImageInput && avatarForm) {
        avatarContainer.addEventListener("click", function () {
            profileImageInput.click();
        });

        profileImageInput.addEventListener("change", function () {
            if (profileImageInput.files && profileImageInput.files[0]) {
                avatarForm.submit();
            }
        });
    }

    // 2. Edit Profile Change Detection
    const usernameInput = document.getElementById("usernameInput");
    const fullNameInput = document.getElementById("fullNameInput");
    const emailInput = document.getElementById("emailInput");
    const bioInput = document.getElementById("bioInput");
    const saveProfileBtn = document.getElementById("saveProfileBtn");
    const editProfileModal = document.getElementById("editProfileModal");

    if (saveProfileBtn && usernameInput && fullNameInput && emailInput && bioInput) {
        let initialValues = {};

        // Snapshot initial values
        function snapshotValues() {
            initialValues = {
                username: usernameInput.value.trim(),
                fullName: fullNameInput.value.trim(),
                email: emailInput.value.trim(),
                bio: bioInput.value.trim()
            };
            evaluateChanges();
        }

        // Compare current values against initial snapshot
        function evaluateChanges() {
            const hasChanged =
                usernameInput.value.trim() !== initialValues.username ||
                fullNameInput.value.trim() !== initialValues.fullName ||
                emailInput.value.trim() !== initialValues.email ||
                bioInput.value.trim() !== initialValues.bio;

            saveProfileBtn.disabled = !hasChanged;
        }

        // Initialize snapshot
        snapshotValues();

        // Refresh snapshot whenever modal opens
        if (editProfileModal) {
            editProfileModal.addEventListener("show.bs.modal", function () {
                snapshotValues();
            });
        }

        // Listen for keystrokes in any of the 4 fields
        [usernameInput, fullNameInput, emailInput, bioInput].forEach(function (input) {
            input.addEventListener("input", evaluateChanges);
        });
    }
});