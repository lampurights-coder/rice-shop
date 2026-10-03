(function () {
  "use strict";

  var eyeSvg =
    '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z"/><circle cx="12" cy="12" r="2.5"/></svg>';

  function ensureModal() {
    var existing = document.getElementById("auth-modal");
    if (existing) {
      // Upgrade old cached modal markup so error UI always exists
      if (!document.getElementById("auth-alert")) {
        var panel = existing.querySelector(".auth-panel");
        var sub = existing.querySelector(".auth-sub");
        if (panel) {
          var alert = document.createElement("div");
          alert.id = "auth-alert";
          alert.className = "auth-alert";
          alert.setAttribute("role", "alert");
          if (sub) sub.insertAdjacentElement("afterend", alert);
          else panel.insertBefore(alert, panel.querySelector("form"));
        }
      }
      existing.querySelectorAll("form.auth-form").forEach(function (form) {
        form.setAttribute("novalidate", "novalidate");
        form.querySelectorAll("input[name]").forEach(function (input) {
          var name = input.getAttribute("name");
          if (!name || form.querySelector('.auth-field-error[data-field="' + name + '"]')) return;
          var p = document.createElement("p");
          p.className = "auth-field-error";
          p.setAttribute("data-field", name);
          var wrap = input.closest(".auth-input-wrap");
          (wrap || input).insertAdjacentElement("afterend", p);
        });
        // old markup used ids without name=
        var phone = form.querySelector("#login-phone, #signup-phone");
        if (phone && !phone.getAttribute("name")) phone.setAttribute("name", "phone");
        var pass = form.querySelector("#login-pass, #signup-pass");
        if (pass && !pass.getAttribute("name")) pass.setAttribute("name", "password");
        var nm = form.querySelector("#signup-name");
        if (nm && !nm.getAttribute("name")) nm.setAttribute("name", "full_name");
        var city = form.querySelector("#signup-city");
        if (city && !city.getAttribute("name")) city.setAttribute("name", "city");
        var postal = form.querySelector("#signup-postal");
        if (postal && !postal.getAttribute("name")) postal.setAttribute("name", "postal_code");
        var addr = form.querySelector("#signup-location");
        if (addr && !addr.getAttribute("name")) addr.setAttribute("name", "address");
      });
      return;
    }

    var wrap = document.createElement("div");
    wrap.id = "auth-modal";
    wrap.className = "auth-modal";
    wrap.setAttribute("aria-hidden", "true");
    wrap.innerHTML =
      '<div class="auth-modal-backdrop" data-auth-close></div>' +
      '<section class="auth-panel" role="dialog" aria-modal="true" aria-labelledby="auth-title">' +
      '<button type="button" class="auth-close" data-auth-close aria-label="بستن">×</button>' +
      '<div class="auth-tabs" role="tablist">' +
      '<button type="button" class="auth-tab is-on" data-mode="login" aria-selected="true">ورود</button>' +
      '<button type="button" class="auth-tab" data-mode="signup" aria-selected="false">ثبت‌نام</button>' +
      "</div>" +
      '<h1 id="auth-title" class="sr-only">ورود</h1>' +
      '<p class="auth-sub" id="auth-sub">خوش برگشتید.</p>' +
      '<div class="auth-alert" id="auth-alert" hidden role="alert"></div>' +
      '<form class="auth-form is-on" id="form-login" novalidate>' +
      '<label class="auth-label" for="login-phone">شماره موبایل</label>' +
      '<input class="auth-input" id="login-phone" name="phone" type="tel" inputmode="numeric" dir="ltr" placeholder="09xxxxxxxxx" autocomplete="username" />' +
      '<p class="auth-field-error" data-field="phone" hidden></p>' +
      '<label class="auth-label" for="login-pass">رمز عبور</label>' +
      '<div class="auth-input-wrap"><input class="auth-input" id="login-pass" name="password" type="password" placeholder="••••••••" autocomplete="current-password" />' +
      '<button type="button" class="auth-eye" data-toggle="#login-pass" aria-label="نمایش رمز">' +
      eyeSvg +
      "</button></div>" +
      '<p class="auth-field-error" data-field="password" hidden></p>' +
      '<div class="auth-row"><label class="auth-check"><input type="checkbox" checked /><span>مرا به خاطر بسپار</span></label>' +
      '<a href="#" class="auth-link">فراموشی رمز؟</a></div>' +
      '<button type="submit" class="auth-btn-primary">ورود ←</button></form>' +
      '<form class="auth-form" id="form-signup" hidden novalidate>' +
      '<label class="auth-label" for="signup-name">نام و نام خانوادگی</label>' +
      '<input class="auth-input" id="signup-name" name="full_name" type="text" placeholder="مثلاً: علی رضایی" autocomplete="name" />' +
      '<p class="auth-field-error" data-field="full_name" hidden></p>' +
      '<label class="auth-label" for="signup-phone">شماره موبایل</label>' +
      '<input class="auth-input" id="signup-phone" name="phone" type="tel" inputmode="numeric" dir="ltr" placeholder="09xxxxxxxxx" autocomplete="tel" />' +
      '<p class="auth-field-error" data-field="phone" hidden></p>' +
      '<div class="auth-grid-2"><div><label class="auth-label" for="signup-city">شهر</label>' +
      '<input class="auth-input" id="signup-city" name="city" type="text" placeholder="مثلاً: رشت" />' +
      '<p class="auth-field-error" data-field="city" hidden></p></div>' +
      '<div><label class="auth-label" for="signup-postal">کد پستی</label>' +
      '<input class="auth-input" id="signup-postal" name="postal_code" type="text" inputmode="numeric" dir="ltr" placeholder="۱۰ رقم" maxlength="10" />' +
      '<p class="auth-field-error" data-field="postal_code" hidden></p></div></div>' +
      '<label class="auth-label" for="signup-location">آدرس / موقعیت</label>' +
      '<input class="auth-input" id="signup-location" name="address" type="text" placeholder="خیابان، کوچه، پلاک..." />' +
      '<p class="auth-field-error" data-field="address" hidden></p>' +
      '<label class="auth-label" for="signup-pass">رمز عبور</label>' +
      '<div class="auth-input-wrap"><input class="auth-input" id="signup-pass" name="password" type="password" placeholder="حداقل ۶ کاراکتر" autocomplete="new-password" />' +
      '<button type="button" class="auth-eye" data-toggle="#signup-pass" aria-label="نمایش رمز">' +
      eyeSvg +
      "</button></div>" +
      '<p class="auth-field-error" data-field="password" hidden></p>' +
      '<button type="submit" class="auth-btn-primary">ثبت‌نام ←</button></form>' +
      '<p class="auth-switch" id="auth-switch">حساب ندارید؟ <button type="button" data-goto="signup">ثبت‌نام کنید</button></p>' +
      '<p class="auth-demo">نسخه نمایشی — اطلاعات ارسال نمی‌شود.</p>' +
      "</section>";

    document.body.appendChild(wrap);
  }

  function setMode(mode) {
    var isLogin = mode === "login";
    var title = document.getElementById("auth-title");
    var sub = document.getElementById("auth-sub");
    var switchEl = document.getElementById("auth-switch");
    var loginForm = document.getElementById("form-login");
    var signupForm = document.getElementById("form-signup");

    document.querySelectorAll(".auth-tab").forEach(function (tab) {
      var on = tab.getAttribute("data-mode") === mode;
      tab.classList.toggle("is-on", on);
      tab.setAttribute("aria-selected", on ? "true" : "false");
    });

    if (loginForm) {
      loginForm.classList.toggle("is-on", isLogin);
      loginForm.hidden = !isLogin;
    }
    if (signupForm) {
      signupForm.classList.toggle("is-on", !isLogin);
      signupForm.hidden = isLogin;
    }
    if (title) title.textContent = isLogin ? "ورود" : "ثبت‌نام";
    if (sub) {
      sub.textContent = isLogin
        ? "خوش برگشتید."
        : "حساب جدید بسازید و سفارش دهید.";
    }
    if (switchEl) {
      switchEl.innerHTML = isLogin
        ? 'حساب ندارید؟ <button type="button" data-goto="signup">ثبت‌نام کنید</button>'
        : 'قبلاً ثبت‌نام کرده‌اید؟ <button type="button" data-goto="login">وارد شوید</button>';
    }
    var alert = document.getElementById("auth-alert");
    if (alert) {
      alert.hidden = true;
      alert.classList.remove("is-on");
      alert.innerHTML = "";
    }
    document.querySelectorAll("#auth-modal .auth-field-error").forEach(function (el) {
      el.hidden = true;
      el.classList.remove("is-on");
      el.textContent = "";
    });
    document.querySelectorAll("#auth-modal .auth-input.is-invalid").forEach(function (el) {
      el.classList.remove("is-invalid");
      el.removeAttribute("aria-invalid");
    });
  }

  function openAuth(mode) {
    ensureModal();
    var modal = document.getElementById("auth-modal");
    setMode(mode === "signup" ? "signup" : "login");
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("auth-modal-open");
  }

  function closeAuth() {
    var modal = document.getElementById("auth-modal");
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("auth-modal-open");
  }

  ensureModal();

  document.addEventListener("click", function (e) {
    var openBtn = e.target.closest("[data-auth-open]");
    if (openBtn) {
      e.preventDefault();
      openAuth(openBtn.getAttribute("data-auth-open") || "login");
      return;
    }

    if (e.target.closest("[data-auth-close]")) {
      closeAuth();
      return;
    }

    var tab = e.target.closest(".auth-tab");
    if (tab && document.getElementById("auth-modal") && document.getElementById("auth-modal").contains(tab)) {
      setMode(tab.getAttribute("data-mode"));
      return;
    }

    var goto = e.target.closest("[data-goto]");
    if (goto && document.getElementById("auth-modal") && document.getElementById("auth-modal").contains(goto)) {
      setMode(goto.getAttribute("data-goto"));
      return;
    }

    var eye = e.target.closest(".auth-eye");
    if (eye) {
      var input = document.querySelector(eye.getAttribute("data-toggle"));
      if (input) input.type = input.type === "password" ? "text" : "password";
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeAuth();
  });

  /* Submit handled by auth-django.js (real API + Persian errors). */

  // Open from query ?auth=login|signup
  var params = new URLSearchParams(window.location.search);
  var authQ = params.get("auth") || params.get("mode");
  if (authQ === "login" || authQ === "signup") {
    openAuth(authQ);
  }

  window.RoudiAuth = { open: openAuth, close: closeAuth };
})();
