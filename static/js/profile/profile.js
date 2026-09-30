document.addEventListener("DOMContentLoaded", function () {
    // 1. Avatar Click Trigger
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

    // 2. Change Detection for Full Name, Email, and Bio
    const fullNameInput = document.getElementById("fullNameInput");
    const emailInput = document.getElementById("emailInput");
    const bioInput = document.getElementById("bioInput");
    const saveProfileBtn = document.getElementById("saveProfileBtn");
    const editProfileModal = document.getElementById("editProfileModal");

    if (saveProfileBtn && fullNameInput && emailInput && bioInput) {
        let initialValues = {};

        function snapshotValues() {
            initialValues = {
                fullName: fullNameInput.value.trim(),
                email: emailInput.value.trim(),
                bio: bioInput.value.trim()
            };
            evaluateChanges();
        }

        function evaluateChanges() {
            const hasChanged =
                fullNameInput.value.trim() !== initialValues.fullName ||
                emailInput.value.trim() !== initialValues.email ||
                bioInput.value.trim() !== initialValues.bio;

            saveProfileBtn.disabled = !hasChanged;
        }

        snapshotValues();

        if (editProfileModal) {
            editProfileModal.addEventListener("show.bs.modal", function () {
                snapshotValues();
            });
        }

        [fullNameInput, emailInput, bioInput].forEach(function (input) {
            input.addEventListener("input", evaluateChanges);
        });
    }
});