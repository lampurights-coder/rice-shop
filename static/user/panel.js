(function () {
  var sidebar = document.getElementById("sidebar");
  var overlay = document.getElementById("sidebarOverlay");
  var menuBtn = document.getElementById("menuBtn");
  var closeBtn = document.getElementById("closeSidebarBtn");
  function openSidebar() {
    if (sidebar) sidebar.classList.add("is-open");
    if (overlay) overlay.classList.add("is-on");
  }
  function closeSidebar() {
    if (sidebar) sidebar.classList.remove("is-open");
    if (overlay) overlay.classList.remove("is-on");
  }
  if (menuBtn) menuBtn.addEventListener("click", openSidebar);
  if (closeBtn) closeBtn.addEventListener("click", closeSidebar);
  if (overlay) overlay.addEventListener("click", closeSidebar);
  var clockEl = document.getElementById("liveClock");
  var dateEl = document.getElementById("todayDate");
  if (clockEl && dateEl) {
    function tick() {
      clockEl.textContent = new Date().toLocaleTimeString("fa-IR", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    }
    dateEl.textContent = new Date().toLocaleDateString("fa-IR", {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
    });
    tick();
    setInterval(tick, 1000);
  }
})();
