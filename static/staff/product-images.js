(function () {
  "use strict";

  var section = document.getElementById("images-section");
  if (!section) return;

  var mode = section.getAttribute("data-mode");
  var productId = section.getAttribute("data-product-id");
  var addUrl = section.getAttribute("data-add-url");
  var picker = document.getElementById("id_image_picker");
  var fileInput = document.getElementById("id_images");
  var pendingBox = document.getElementById("pending-previews");
  var library = document.getElementById("image-library");
  var primaryNew = document.getElementById("primary_new");
  var primaryImage = document.getElementById("primary_image");
  var csrf =
    (document.querySelector("[name=csrfmiddlewaretoken]") || {}).value ||
    (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] ||
    "";

  var staged = []; // { file, url, primary }

  function syncFileInput() {
    if (!fileInput || !window.DataTransfer) return;
    var dt = new DataTransfer();
    staged.forEach(function (item) {
      dt.items.add(item.file);
    });
    fileInput.files = dt.files;
    var pIdx = staged.findIndex(function (s) {
      return s.primary;
    });
    if (primaryNew) primaryNew.value = pIdx >= 0 ? String(pIdx) : "";
  }

  function renderPending() {
    if (!pendingBox) return;
    pendingBox.innerHTML = "";
    staged.forEach(function (item, idx) {
      var card = document.createElement("article");
      card.className = "img-card" + (item.primary ? " is-primary" : "");
      card.innerHTML =
        '<img src="' +
        item.url +
        '" alt="" />' +
        (item.primary ? '<span class="img-badge">اصلی</span>' : "") +
        '<button type="button" class="img-btn-primary" data-pending-primary="' +
        idx +
        '">تصویر اصلی</button>' +
        '<button type="button" class="img-btn-delete" data-pending-remove="' +
        idx +
        '">حذف</button>';
      pendingBox.appendChild(card);
    });
    syncFileInput();
  }

  function markLibraryPrimary(id) {
    if (!library) return;
    library.querySelectorAll(".img-card").forEach(function (card) {
      var on = String(card.getAttribute("data-id")) === String(id);
      card.classList.toggle("is-primary", on);
      var badge = card.querySelector(".img-badge");
      if (on && !badge) {
        var b = document.createElement("span");
        b.className = "img-badge";
        b.textContent = "اصلی";
        card.appendChild(b);
      } else if (!on && badge) {
        badge.remove();
      }
    });
    if (primaryImage) primaryImage.value = id ? String(id) : "";
    staged.forEach(function (s) {
      s.primary = false;
    });
    renderPending();
  }

  function appendLibraryCard(data) {
    if (!library) return;
    var card = document.createElement("article");
    card.className = "img-card" + (data.is_primary ? " is-primary" : "");
    card.setAttribute("data-id", data.id);
    card.innerHTML =
      '<img src="' +
      data.url +
      '" alt="" />' +
      (data.is_primary ? '<span class="img-badge">اصلی</span>' : "") +
      '<button type="button" class="img-btn-primary" data-action="primary" data-id="' +
      data.id +
      '">تصویر اصلی</button>' +
      '<button type="button" class="img-btn-delete" data-action="delete" data-id="' +
      data.id +
      '">حذف</button>';
    library.appendChild(card);
    if (data.is_primary) markLibraryPrimary(data.id);
  }

  function uploadOne(file, makePrimary) {
    if (!addUrl) return Promise.reject();
    var body = new FormData();
    body.append("image", file);
    if (makePrimary) body.append("make_primary", "1");
    return fetch(addUrl, {
      method: "POST",
      headers: { "X-CSRFToken": csrf },
      body: body,
      credentials: "same-origin",
    }).then(function (r) {
      return r.json();
    });
  }

  if (picker) {
    picker.addEventListener("change", function () {
      var file = picker.files && picker.files[0];
      picker.value = "";
      if (!file || !file.type.startsWith("image/")) return;

      // Edit mode: upload immediately, one by one
      if (mode === "edit" && productId && addUrl) {
        var makePrimary = !library || !library.querySelector(".img-card");
        uploadOne(file, makePrimary).then(function (data) {
          if (!data || !data.ok) {
            alert((data && data.error) || "آپلود تصویر ناموفق بود");
            return;
          }
          appendLibraryCard(data);
        });
        return;
      }

      // Create mode: stage files step-by-step, submit with form
      var url = URL.createObjectURL(file);
      var isFirst = staged.length === 0;
      staged.push({ file: file, url: url, primary: isFirst });
      renderPending();
    });
  }

  if (pendingBox) {
    pendingBox.addEventListener("click", function (e) {
      var pBtn = e.target.closest("[data-pending-primary]");
      var rBtn = e.target.closest("[data-pending-remove]");
      if (pBtn) {
        var pi = parseInt(pBtn.getAttribute("data-pending-primary"), 10);
        staged.forEach(function (s, i) {
          s.primary = i === pi;
        });
        if (primaryImage) primaryImage.value = "";
        renderPending();
      }
      if (rBtn) {
        var ri = parseInt(rBtn.getAttribute("data-pending-remove"), 10);
        staged.splice(ri, 1);
        if (staged.length && !staged.some(function (s) { return s.primary; })) {
          staged[0].primary = true;
        }
        renderPending();
      }
    });
  }

  if (library) {
    library.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-action]");
      if (!btn || !productId) return;
      var id = btn.getAttribute("data-id");
      var action = btn.getAttribute("data-action");
      if (action === "primary") {
        fetch("/staff/products/" + productId + "/images/" + id + "/primary/", {
          method: "POST",
          headers: { "X-CSRFToken": csrf },
          credentials: "same-origin",
        })
          .then(function (r) {
            return r.json();
          })
          .then(function (data) {
            if (data && data.ok) markLibraryPrimary(id);
          });
      }
      if (action === "delete") {
        if (!confirm("این تصویر حذف شود؟")) return;
        fetch("/staff/products/" + productId + "/images/" + id + "/delete/", {
          method: "POST",
          headers: { "X-CSRFToken": csrf },
          credentials: "same-origin",
        })
          .then(function (r) {
            return r.json();
          })
          .then(function (data) {
            if (!data || !data.ok) return;
            var card = library.querySelector('.img-card[data-id="' + id + '"]');
            if (card) card.remove();
            if (data.primary_id) markLibraryPrimary(data.primary_id);
          });
      }
    });
  }
})();
