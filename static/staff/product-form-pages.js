(function () {
  "use strict";

  var tabs = Array.prototype.slice.call(document.querySelectorAll(".form-page-tab"));
  var panels = Array.prototype.slice.call(document.querySelectorAll("[data-page-panel]"));
  var prevBtn = document.getElementById("page-prev");
  var nextBtn = document.getElementById("page-next");
  var saveBtn = document.getElementById("page-save");
  var page = 1;
  var total = panels.length || 5;

  function show(n) {
    page = Math.max(1, Math.min(total, n));
    tabs.forEach(function (t) {
      t.classList.toggle("is-on", Number(t.getAttribute("data-page")) === page);
    });
    panels.forEach(function (p) {
      var on = Number(p.getAttribute("data-page-panel")) === page;
      p.hidden = !on;
      p.classList.toggle("is-on", on);
    });
    if (prevBtn) prevBtn.hidden = page === 1;
    if (nextBtn) nextBtn.hidden = page === total;
    if (saveBtn) saveBtn.hidden = page !== total;
    renumberCook();
  }

  tabs.forEach(function (t) {
    t.addEventListener("click", function () {
      show(Number(t.getAttribute("data-page")));
    });
  });
  if (prevBtn) prevBtn.addEventListener("click", function () { show(page - 1); });
  if (nextBtn) nextBtn.addEventListener("click", function () { show(page + 1); });

  function renumberCook() {
    document.querySelectorAll("#cook-list .list-step-num").forEach(function (el, i) {
      el.textContent = (i + 1).toLocaleString("fa-IR");
    });
  }

  function bindList(listId, inputId, addId, name, withNum) {
    var list = document.getElementById(listId);
    var input = document.getElementById(inputId);
    var add = document.getElementById(addId);
    if (!list || !input || !add) return;

    function addItem(value) {
      var text = (value || "").trim();
      if (!text) return;
      var li = document.createElement("li");
      var html = "";
      if (withNum) html += '<span class="list-step-num"></span>';
      html +=
        '<input class="staff-input" type="text" name="' +
        name +
        '" value="' +
        text.replace(/"/g, "&quot;") +
        '" />' +
        '<button type="button" class="list-remove" aria-label="حذف">×</button>';
      li.innerHTML = html;
      list.appendChild(li);
      input.value = "";
      input.focus();
      renumberCook();
    }

    add.addEventListener("click", function () {
      addItem(input.value);
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        addItem(input.value);
      }
    });
    list.addEventListener("click", function (e) {
      var btn = e.target.closest(".list-remove");
      if (!btn) return;
      btn.closest("li").remove();
      renumberCook();
    });
  }

  bindList("features-list", "feature-input", "feature-add", "features", false);
  bindList("cook-list", "cook-input", "cook-add", "cook_steps", true);

  show(1);
})();
