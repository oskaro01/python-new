const realtimeMessageList = document.querySelector(".message-list");
const realtimeFeedback = document.querySelector("#composer-feedback");

if (realtimeMessageList && realtimeMessageList.dataset.conversationId) {
    const scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${scheme}://${window.location.host}/ws/chat/conversations/${realtimeMessageList.dataset.conversationId}/`;
    const socket = new WebSocket(socketUrl);
    window.chatRealtimeSocket = socket;

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

        const body = document.createElement("div");
        body.textContent = payload.body;
        article.appendChild(body);

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

    socket.addEventListener("message", (event) => {
        const payload = JSON.parse(event.data);
        if (payload.type === "message") appendRealtimeMessage(payload);
        if (payload.type === "error" && realtimeFeedback) {
            realtimeFeedback.textContent = payload.error;
            realtimeFeedback.style.color = "";
            realtimeFeedback.hidden = false;
        }
    });

    window.chatRealtimeSend = (body) => {
        if (socket.readyState !== WebSocket.OPEN || !body.trim() || body.length > 5000) {
            return false;
        }
        socket.send(JSON.stringify({ body }));
        return true;
    };
}
