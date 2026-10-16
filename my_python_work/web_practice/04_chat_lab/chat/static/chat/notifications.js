(function () {
    const countElement = document.querySelector("#topbar-chat-count");
    const friendsCountElement = document.querySelector("#topbar-friends-count");
    const currentConversation = document.querySelector(".message-list")?.dataset.conversationId;
    const scheme = window.location.protocol === "https:" ? "wss" : "ws";
    let socket;
    let reconnectTimer;
    let reconnectDelay = 1000;

    function updateTopbarCount() {
        if (!countElement) return;
        const current = Number(countElement.dataset.count || 0);
        const next = current + 1;
        countElement.dataset.count = String(next);
        countElement.textContent = `(${next})`;
    }

    function updateFriendsCount() {
        if (!friendsCountElement) return;
        const current = Number(friendsCountElement.dataset.count || 0);
        const next = current + 1;
        friendsCountElement.dataset.count = String(next);
        friendsCountElement.textContent = `(${next})`;
    }

    function updateConversationBadge(payload) {
        const row = document.querySelector(`[data-conversation-id="${payload.conversation_id}"]`);
        if (!row) return;

        let badge = row.querySelector(".unread-badge");
        if (!badge) {
            badge = document.createElement("b");
            badge.id = `unread-${payload.conversation_id}`;
            badge.className = "unread-badge";
            row.appendChild(badge);
        }
        badge.textContent = String(Number(badge.textContent || 0) + 1);
    }

    function connect() {
        socket = new WebSocket(`${scheme}://${window.location.host}/ws/notifications/`);

        socket.addEventListener("open", () => {
            reconnectDelay = 1000;
        });

        socket.addEventListener("message", (event) => {
            const payload = JSON.parse(event.data);
            if (payload.type === "friend_request") {
                updateFriendsCount();
                return;
            }
            if (payload.type !== "notification") return;
            if (String(payload.conversation_id) === String(currentConversation)) return;

            updateTopbarCount();
            updateConversationBadge(payload);
        });

        socket.addEventListener("error", () => socket.close());
        socket.addEventListener("close", () => {
            window.clearTimeout(reconnectTimer);
            reconnectTimer = window.setTimeout(connect, reconnectDelay);
            reconnectDelay = Math.min(reconnectDelay * 2, 10000);
        });
    }

    connect();
})();
