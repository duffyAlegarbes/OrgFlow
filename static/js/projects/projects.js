document.addEventListener("DOMContentLoaded", function () {
    // Automatically set widths for any progress bars with data-percentage
    const progressBars = document.querySelectorAll(".dynamic-progress");
    progressBars.forEach(function (bar) {
        const percentage = bar.getAttribute("data-percentage") || "0";
        bar.style.width = percentage + "%";
    });
});