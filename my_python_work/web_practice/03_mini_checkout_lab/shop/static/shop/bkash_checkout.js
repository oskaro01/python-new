(function () {
    const button = document.querySelector("#bkash_button");
    if (!button) return;

    const feedback = document.querySelector("#bkash-feedback");
    const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']")?.value || "";
    function showError(message) {
        if (feedback) feedback.textContent = message;
    }

    async function post(url, data) {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken,
            },
            body: new URLSearchParams(data),
        });
        const result = await response.json();
        if (!response.ok || result.ok === false) {
            throw new Error(result.error || "bKash payment request failed.");
        }
        return result;
    }

    button.addEventListener("click", async () => {
        button.disabled = true;
        showError("Preparing secure bKash checkout...");
        try {
            const result = await post(button.dataset.createUrl, {});
            if (!result.bkashURL) throw new Error("bKash did not return a checkout URL.");
            window.location.assign(result.bkashURL);
        } catch (error) {
            button.disabled = false;
            showError(error.message);
        }
    });
})();
