(() => {
    const toastStack = document.querySelector(".toast-stack");

    function showToast(message, isError = false) {
        if (!toastStack) return;

        const toast = document.createElement("div");
        toast.className = isError ? "toast toast-error" : "toast";
        toast.textContent = message;
        toastStack.appendChild(toast);

        requestAnimationFrame(() => toast.classList.add("is-visible"));
        window.setTimeout(() => {
            toast.classList.remove("is-visible");
            window.setTimeout(() => toast.remove(), 180);
        }, 3200);
    }

    function updateCartCount(count) {
        document.querySelectorAll(".cart-count").forEach((element) => {
            element.textContent = count;
        });
    }

    document.querySelectorAll(".js-add-to-cart").forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const button = form.querySelector("button[type=submit]");
            const originalLabel = button ? button.textContent : "";
            if (button) {
                button.disabled = true;
                button.textContent = "Adding...";
            }

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    headers: {
                        "Accept": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    credentials: "same-origin",
                    body: new FormData(form),
                });
                const data = await response.json();

                if (!response.ok || !data.ok) {
                    throw new Error(data.message || "The product could not be added.");
                }

                updateCartCount(data.cart_count);
                showToast(data.message);
            } catch (error) {
                showToast(error.message, true);
            } finally {
                if (button) {
                    button.disabled = false;
                    button.textContent = originalLabel;
                }
            }
        });
    });
})();
