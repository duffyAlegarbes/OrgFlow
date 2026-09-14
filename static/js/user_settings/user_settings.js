document.addEventListener("DOMContentLoaded", function () {
    const saveSettingsBtn = document.getElementById("saveSettingsBtn");
    const settingInputs = document.querySelectorAll(".setting-input");

    if (saveSettingsBtn && settingInputs.length > 0) {
        // Record initial state of all settings inputs
        const initialStates = new Map();

        settingInputs.forEach(input => {
            if (input.type === "checkbox") {
                initialStates.set(input, input.checked);
            } else {
                initialStates.set(input, input.value);
            }
        });

        // Function to detect if any setting differs from initial state
        function checkForChanges() {
            let hasChanged = false;

            settingInputs.forEach(input => {
                if (input.type === "checkbox") {
                    if (input.checked !== initialStates.get(input)) {
                        hasChanged = true;
                    }
                } else {
                    if (input.value !== initialStates.get(input)) {
                        hasChanged = true;
                    }
                }
            });

            // Toggle save button enabled/disabled
            saveSettingsBtn.disabled = !hasChanged;
        }

        // Listen for toggle / selection changes
        settingInputs.forEach(input => {
            input.addEventListener("change", checkForChanges);
            input.addEventListener("input", checkForChanges);
        });
    }
});