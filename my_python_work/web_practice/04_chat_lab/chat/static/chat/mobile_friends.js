(function () {
    const toggles = Array.from(document.querySelectorAll("[data-mobile-drawer-toggle]"));
    const sidebar = document.querySelector("#friends-sidebar");
    const backdrop = document.querySelector("#friends-drawer-backdrop");
    if (!toggles.length) return;

    // Pages without the sidebar (such as profile settings) use these controls
    // as a clear route back to the chat home.
    if (!sidebar || !backdrop) {
        toggles.forEach((toggle) => {
            toggle.addEventListener("click", () => {
                if (toggle.dataset.homeUrl) window.location.assign(toggle.dataset.homeUrl);
            });
        });
        return;
    }

    function syncTopbarHeight() {
        const topbar = document.querySelector(".fb-topbar");
        if (topbar) {
            document.documentElement.style.setProperty(
                "--mobile-topbar-height",
                `${topbar.offsetHeight}px`
            );
        }
    }

    function setOpen(open) {
        document.body.classList.toggle("mobile-friends-open", open);
        toggles.forEach((toggle) => toggle.setAttribute("aria-expanded", String(open)));
    }

    toggles.forEach((toggle) => toggle.addEventListener("click", () => {
        if (!window.matchMedia("(max-width: 700px)").matches) {
            if (toggle.id === "mobile-chats-toggle" && toggle.dataset.homeUrl) {
                window.location.assign(toggle.dataset.homeUrl);
            }
            return;
        }
        setOpen(!document.body.classList.contains("mobile-friends-open"));
    }));
    backdrop.addEventListener("click", () => setOpen(false));
    syncTopbarHeight();
    window.addEventListener("resize", syncTopbarHeight);
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") setOpen(false);
    });
})();
