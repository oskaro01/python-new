const composer = document.querySelector("#message-composer");
const messageList = document.querySelector(".message-list");
const feedback = document.querySelector("#composer-feedback");

if (composer && messageList) {
    composer.addEventListener("submit", async (event) => {
        event.preventDefault();
        const sendButton = composer.querySelector("button[type='submit']");
        sendButton.disabled = true;
        feedback.hidden = true;

        try {
            const bodyField = composer.querySelector("[name='body']");
            const attachmentField = composer.querySelector("input[type='file']");
            const hasAttachment = attachmentField && attachmentField.files.length > 0;
            if (
                !hasAttachment
                && window.chatRealtimeSend
                && window.chatRealtimeSend(bodyField.value)
            ) {
                composer.reset();
                return;
            }

            const response = await fetch(composer.action || window.location.href, {
                method: "POST",
                body: new FormData(composer),
                headers: {
                    "X-Chat-Async": "1",
                    "X-Requested-With": "XMLHttpRequest",
                },
            });
            const payload = await response.json();

            if (!response.ok || !payload.ok) {
                throw new Error(payload.error || "Message could not be sent.");
            }

            composer.reset();

            // Search and older pages must keep their own message selection.
            if (messageList.dataset.canAppend !== "true") {
                feedback.textContent = "Sent. Open Latest messages to see your message.";
                feedback.style.color = "#3b5998";
                feedback.hidden = false;
                return;
            }

            // The WebSocket broadcast can arrive before this HTTP response.
            // Use the durable ID to avoid inserting the same message twice.
            if (
                payload.message_id
                && document.querySelector(`[data-message-id="${payload.message_id}"]`)
            ) {
                return;
            }

            const emptyState = messageList.querySelector(".intro");
            if (emptyState) emptyState.remove();
            messageList.insertAdjacentHTML("beforeend", payload.html);
            // Keep the newest page bounded even after many asynchronous sends.
            while (messageList.querySelectorAll(".message").length > 20) {
                messageList.querySelector(".message").remove();
            }
            const pagination = document.querySelector("#message-pagination");
            if (pagination && payload.pagination_html) pagination.innerHTML = payload.pagination_html;
            messageList.scrollTop = messageList.scrollHeight;

            // Register the same expiry behavior for the newly inserted bubble.
            const newMessage = messageList.lastElementChild;
            if (newMessage) {
                const deadline = Number(newMessage.dataset.expiresAt) * 1000;
                window.setTimeout(() => newMessage.remove(), Math.max(0, deadline - Date.now()));
            }
        } catch (error) {
            feedback.textContent = error.message;
            feedback.style.color = "";
            feedback.hidden = false;
        } finally {
            sendButton.disabled = false;
        }
    });
}
