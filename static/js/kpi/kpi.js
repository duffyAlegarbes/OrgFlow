document.addEventListener("DOMContentLoaded", function () {
    // Dynamic progress bar styling with zero editor linter errors
    const progressBars = document.querySelectorAll(".dynamic-progress");
    progressBars.forEach(function (bar) {
        const percentage = bar.getAttribute("data-percentage") || "0";
        bar.style.width = percentage + "%";
    });
});