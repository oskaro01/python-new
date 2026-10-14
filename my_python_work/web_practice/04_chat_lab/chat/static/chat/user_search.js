(function () {
    const chatInput = document.querySelector("#conversation-search");
    const chatRows = [...document.querySelectorAll("[data-chat-search]")];
    if (chatInput) {
        chatInput.addEventListener("input", () => {
            const query = chatInput.value.trim().toLocaleLowerCase();
            chatRows.forEach((row) => {
                row.hidden = !row.dataset.chatSearch.toLocaleLowerCase().includes(query);
            });
            document.querySelector("#chat-search-empty").hidden =
                !query || chatRows.some((row) => !row.hidden);
        });
    }

    const input = document.querySelector("#topbar-user-search");
    const results = document.querySelector("#user-suggestions");
    if (!input || !results) return;
    let timer;
    let searchVersion = 0;

    function message(text) {
        const node = document.createElement("p");
        node.className = "search-feedback";
        node.textContent = text;
        results.replaceChildren(node);
        results.hidden = false;
    }

    function endpoint(template, id) {
        return template.replace("/0/", "/" + id + "/");
    }

    function actionForm(url, labels) {
        const form = document.createElement("form");
        form.method = "post";
        form.action = url;
        const csrf = document.createElement("input");
        csrf.type = "hidden";
        csrf.name = "csrfmiddlewaretoken";
        csrf.value = results.dataset.csrfToken;
        form.appendChild(csrf);
        labels.forEach(([label, value]) => {
            const button = document.createElement("button");
            button.type = "submit";
            button.className = "add-button" + (value === "decline" ? " decline-button" : "");
            button.textContent = label;
            if (value) {
                button.name = "action";
                button.value = value;
            }
            form.appendChild(button);
        });
        return form;
    }

    function renderUsers(users) {
        results.replaceChildren();
        results.hidden = false;
        if (!users.length) {
            message("No matching people.");
            return;
        }
        users.forEach((user) => {
            const row = document.createElement("div");
            row.className = "user-result";
            const avatar = document.createElement(user.avatar_url ? "img" : "span");
            avatar.className = "avatar avatar-small";
            if (user.avatar_url) {
                avatar.classList.add("avatar-image");
                avatar.src = user.avatar_url;
                avatar.alt = "";
            } else {
                avatar.textContent = user.initial;
            }
            const name = document.createElement("strong");
            name.className = "user-result-name";
            name.textContent = user.name;
            const actions = document.createElement("div");
            actions.className = "friend-actions";
            if (user.status === "incoming") {
                actions.appendChild(actionForm(
                    endpoint(results.dataset.responseUrlTemplate, user.request_id),
                    [["Accept", "accept"], ["Decline", "decline"]]
                ));
            } else if (user.status === "friends") {
                actions.appendChild(actionForm(
                    endpoint(results.dataset.startUrlTemplate, user.id), [["Chat"]]
                ));
            } else {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "add-button";
                button.textContent = user.status === "pending" ? "Pending" : "Add";
                button.disabled = user.status === "pending";
                button.addEventListener("click", () => sendRequest(button, user.id));
                actions.appendChild(button);
            }
            row.append(avatar, name, actions);
            results.appendChild(row);
        });
    }

    async function search(version) {
        const query = input.value.trim();
        if (!query) {
            results.replaceChildren();
            results.hidden = true;
            return;
        }
        message("Searching...");
        try {
            const response = await fetch(results.dataset.searchUrl + "?q=" + encodeURIComponent(query), {
                headers: { Accept: "application/json" },
            });
            if (!response.ok) throw new Error("Search failed");
            const data = await response.json();
            if (version === searchVersion) renderUsers(data.users);
        } catch (error) {
            if (version === searchVersion) message("Search is unavailable. Please try again.");
        }
    }

    async function sendRequest(button, userId) {
        button.disabled = true;
        try {
            const response = await fetch(endpoint(results.dataset.requestUrlTemplate, userId), {
                method: "POST",
                headers: {
                    "X-CSRFToken": results.dataset.csrfToken,
                    Accept: "application/json",
                },
            });
            if (!response.ok) throw new Error("Request failed");
            const data = await response.json();
            if (data.status === "pending") {
                button.textContent = "Pending";
            } else {
                await search(++searchVersion);
            }
        } catch (error) {
            button.disabled = false;
            button.textContent = "Retry";
            button.title = "Request failed. Click to retry.";
        }
    }

    input.addEventListener("input", () => {
        window.clearTimeout(timer);
        const version = ++searchVersion;
        if (!input.value.trim()) {
            results.replaceChildren();
            results.hidden = true;
            return;
        }
        timer = window.setTimeout(() => search(version), 250);
    });
    input.form.addEventListener("submit", (event) => {
        event.preventDefault();
        window.clearTimeout(timer);
        search(++searchVersion);
    });
    input.addEventListener("focus", () => {
        if (input.value.trim() && results.childElementCount) results.hidden = false;
    });
    input.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            ++searchVersion;
            window.clearTimeout(timer);
            results.hidden = true;
        }
    });
    document.addEventListener("click", (event) => {
        if (!input.form.contains(event.target) && !results.contains(event.target)) results.hidden = true;
    });
})();
