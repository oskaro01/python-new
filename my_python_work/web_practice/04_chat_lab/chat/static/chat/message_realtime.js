const realtimeMessageList = document.querySelector(".message-list");
const realtimeFeedback = document.querySelector("#composer-feedback");

if (realtimeMessageList && realtimeMessageList.dataset.conversationId) {
    const scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${scheme}://${window.location.host}/ws/chat/conversations/${realtimeMessageList.dataset.conversationId}/`;
    let socket;
    let reconnectTimer;
    let reconnectDelay = 1000;

    function appendRealtimeMessage(payload) {
        if (realtimeMessageList.dataset.canAppend !== "true") {
            if (realtimeFeedback) {
                realtimeFeedback.textContent = "New message available. Open Latest messages to see it.";
                realtimeFeedback.style.color = "#3b5998";
                realtimeFeedback.hidden = false;
            }
            return;
        }
        if (document.querySelector(`[data-message-id="${payload.message_id}"]`)) return;

        const article = document.createElement("article");
        article.dataset.messageId = payload.message_id;
        article.dataset.expiresAt = payload.expires_at;
        article.className = `message ${String(payload.sender_id) === realtimeMessageList.dataset.userId ? "message-own" : "message-other"}`;

        const sender = document.createElement("strong");
        sender.textContent = payload.sender_name;
        article.appendChild(sender);

        if (payload.body) {
            const body = document.createElement("div");
            body.textContent = payload.body;
            article.appendChild(body);
        }

        for (const attachment of payload.attachments || []) {
            const attachmentBox = document.createElement("div");
            attachmentBox.className = "message-attachment";

            const previewLink = document.createElement("a");
            previewLink.href = attachment.url;
            previewLink.target = "_blank";
            previewLink.rel = "noopener";

            const image = document.createElement("img");
            image.src = attachment.url;
            image.alt = attachment.original_name;
            image.loading = "lazy";
            previewLink.appendChild(image);
            attachmentBox.appendChild(previewLink);

            const downloadLink = document.createElement("a");
            downloadLink.className = "attachment-download";
            downloadLink.href = attachment.download_url;
            downloadLink.textContent = `Download ${attachment.original_name}`;
            attachmentBox.appendChild(downloadLink);
            article.appendChild(attachmentBox);
        }

        const footer = document.createElement("small");
        footer.textContent = new Date(payload.created_at).toLocaleString();
        article.appendChild(footer);
        realtimeMessageList.appendChild(article);

        while (realtimeMessageList.querySelectorAll(".message").length > 20) {
            realtimeMessageList.querySelector(".message").remove();
        }
        realtimeMessageList.scrollTop = realtimeMessageList.scrollHeight;
        window.setTimeout(() => article.remove(), Math.max(0, payload.expires_at * 1000 - Date.now()));
    }

    function connect() {
        socket = new WebSocket(socketUrl);
        window.chatRealtimeSocket = socket;

        socket.addEventListener("open", () => {
            reconnectDelay = 1000;
        });

        socket.addEventListener("message", (event) => {
            const payload = JSON.parse(event.data);
            if (payload.type === "message") appendRealtimeMessage(payload);
            if (payload.type === "error" && realtimeFeedback) {
                realtimeFeedback.textContent = payload.error;
                realtimeFeedback.style.color = "";
                realtimeFeedback.hidden = false;
            }
        });

        socket.addEventListener("error", () => socket.close());
        socket.addEventListener("close", () => {
            window.clearTimeout(reconnectTimer);
            reconnectTimer = window.setTimeout(connect, reconnectDelay);
            reconnectDelay = Math.min(reconnectDelay * 2, 10000);
        });
    }

    connect();

    window.chatRealtimeSend = (body) => {
        if (socket.readyState !== WebSocket.OPEN || !body.trim() || body.length > 5000) {
            return false;
        }
        socket.send(JSON.stringify({ body }));
        return true;
    };
}
