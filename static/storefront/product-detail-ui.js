(function () {
  "use strict";

  document.querySelectorAll(".pd-tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      var name = tab.getAttribute("data-tab");
      document.querySelectorAll(".pd-tab").forEach(function (t) {
        var on = t === tab;
        t.classList.toggle("is-on", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
      });
      document.querySelectorAll(".pd-tab-panel").forEach(function (panel) {
        var on = panel.getAttribute("data-panel") === name;
        panel.classList.toggle("is-on", on);
        panel.hidden = !on;
      });
    });
  });

  var pack = document.getElementById("pack-img");
  document.querySelectorAll(".pd-thumbs button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".pd-thumbs button").forEach(function (b) {
        b.classList.remove("is-on");
      });
      btn.classList.add("is-on");
      var src = btn.getAttribute("data-src");
      if (pack && src) pack.src = src;
    });
  });
})();
