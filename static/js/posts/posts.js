document.addEventListener("DOMContentLoaded", function () {
    const postTypeSelect = document.getElementById("postTypeSelect");
    const partnershipFields = document.getElementById("partnershipFields");

    if (postTypeSelect && partnershipFields) {
        function togglePartnershipFields() {
            if (postTypeSelect.value === "Partnership") {
                partnershipFields.classList.remove("d-none");
            } else {
                partnershipFields.classList.add("d-none");
            }
        }

        // Initial check and change listener
        togglePartnershipFields();
        postTypeSelect.addEventListener("change", togglePartnershipFields);
    }
});