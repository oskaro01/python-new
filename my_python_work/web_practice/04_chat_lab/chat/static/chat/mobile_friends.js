(function () {
    const toggle = document.querySelector("#mobile-friends-toggle");
    const sidebar = document.querySelector("#friends-sidebar");
    const backdrop = document.querySelector("#friends-drawer-backdrop");
    if (!toggle || !sidebar || !backdrop) return;

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
        toggle.setAttribute("aria-expanded", String(open));
    }

    toggle.addEventListener("click", () => {
        setOpen(!document.body.classList.contains("mobile-friends-open"));
    });
    backdrop.addEventListener("click", () => setOpen(false));
    syncTopbarHeight();
    window.addEventListener("resize", syncTopbarHeight);
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") setOpen(false);
    });
})();
