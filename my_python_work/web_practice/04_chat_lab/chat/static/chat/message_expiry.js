// Remove already-rendered messages at their deadline without polling Django.
// The server separately enforces expiry and the cleanup process deletes data.
document.querySelectorAll("[data-expires-at]").forEach((message) => {
    const deadline = Number(message.dataset.expiresAt) * 1000;
    function expire() {
        const remaining = deadline - Date.now();
        if (remaining <= 0) {
            message.remove();
        } else {
            window.setTimeout(expire, Math.min(remaining, 2147483647));
        }
    }
    expire();
});
