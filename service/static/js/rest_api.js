document.addEventListener("DOMContentLoaded", () => {
    const fieldIds = [
        "order_id",
        "order_customer_id",
        "order_name",
        "order_address",
        "order_email",
        "order_status",
    ];

    const clearButton = document.getElementById("clear-btn");
    const flashMessage = document.getElementById("flash_message");

    function clearFormData() {
        document.getElementById("order_id").value = "";
        document.getElementById("order_customer_id").value = "";
        document.getElementById("order_name").value = "";
        document.getElementById("order_address").value = "";
        document.getElementById("order_email").value = "";
        document.getElementById("order_status").value = "Pending";
    }

    if (clearButton) {
        clearButton.addEventListener("click", () => {
            clearFormData();
            if (flashMessage) {
                flashMessage.textContent = "Form cleared";
            }
        });
    }

    // Placeholder only for setup story.
    // CRUD / query / action handlers will be added in later UI stories.
    fieldIds.forEach((fieldId) => {
        const element = document.getElementById(fieldId);
        if (!element) {
            console.warn(`Missing expected field: ${fieldId}`);
        }
    });
});