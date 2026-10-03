(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var demo = document.querySelector(".auth-demo");
    if (demo) demo.hidden = true;
  });

  function getCookie(name) {
    var m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return m ? decodeURIComponent(m[2]) : "";
  }

  function csrfToken() {
    var input = document.querySelector("[name=csrfmiddlewaretoken]");
    return (input && input.value) || getCookie("csrftoken") || "";
  }

  function panelOf(form) {
    return (form && form.closest(".auth-panel")) || document.querySelector("#auth-modal .auth-panel");
  }

  function ensureErrorUi(form) {
    if (!form) return null;
    var panel = panelOf(form);
    var alert = document.getElementById("auth-alert");
    if (!alert && panel) {
      alert = document.createElement("div");
      alert.id = "auth-alert";
      alert.className = "auth-alert";
      alert.setAttribute("role", "alert");
      var sub = panel.querySelector(".auth-sub");
      if (sub) sub.insertAdjacentElement("afterend", alert);
      else panel.insertBefore(alert, form);
    }

    form.querySelectorAll("input[name]").forEach(function (input) {
      var name = input.getAttribute("name");
      if (!name || form.querySelector('.auth-field-error[data-field="' + name + '"]')) return;
      var p = document.createElement("p");
      p.className = "auth-field-error";
      p.setAttribute("data-field", name);
      var wrap = input.closest(".auth-input-wrap");
      (wrap || input).insertAdjacentElement("afterend", p);
    });
    return alert;
  }

  function shake(form) {
    var panel = panelOf(form);
    if (!panel) return;
    panel.classList.remove("is-shake");
    void panel.offsetWidth;
    panel.classList.add("is-shake");
    setTimeout(function () {
      panel.classList.remove("is-shake");
    }, 520);
  }

  function clearFormErrors(form) {
    if (!form) return;
    ensureErrorUi(form);
    form.querySelectorAll(".auth-field-error").forEach(function (el) {
      el.classList.remove("is-on");
      el.hidden = true;
      el.textContent = "";
    });
    form.querySelectorAll(".auth-input.is-invalid").forEach(function (el) {
      el.classList.remove("is-invalid");
    });
    var alert = document.getElementById("auth-alert");
    if (alert) {
      alert.classList.remove("is-on");
      alert.hidden = true;
      alert.innerHTML = "";
    }
  }

  function showFieldError(form, fieldKey, message) {
    ensureErrorUi(form);
    var input = form.querySelector('[name="' + fieldKey + '"]');
    var box = form.querySelector('.auth-field-error[data-field="' + fieldKey + '"]');
    if (input) {
      input.classList.add("is-invalid");
      input.setAttribute("aria-invalid", "true");
    }
    if (box) {
      box.textContent = message;
      box.hidden = false;
      box.classList.add("is-on");
    }
  }

  function showBanner(form, message) {
    var alert = ensureErrorUi(form);
    if (!alert) return;
    alert.innerHTML =
      '<span class="auth-alert-mark" aria-hidden="true">!</span>' +
      '<div class="auth-alert-body">' +
      '<strong>ورود انجام نشد</strong>' +
      "<span>" +
      message +
      "</span>" +
      "</div>";
    alert.hidden = false;
    alert.classList.add("is-on");
    shake(form);
  }

  function showErrors(form, payload) {
    clearFormErrors(form);
    var message = (payload && payload.message) || "شماره یا رمز عبور را دوباره بررسی کنید";
    var errors = (payload && payload.errors) || {};
    showBanner(form, message);
    Object.keys(errors).forEach(function (key) {
      if (key === "__all__") return;
      var list = errors[key];
      var text = Array.isArray(list) ? list[0] : list;
      if (text) showFieldError(form, key, text);
    });
  }

  function validPhone(v) {
    return /^09\d{9}$/.test(String(v || "").trim());
  }

  function postAuth(url, data) {
    var body = new URLSearchParams(data);
    var token = csrfToken();
    if (token) body.append("csrfmiddlewaretoken", token);
    return fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": token,
        "X-Requested-With": "XMLHttpRequest",
        Accept: "application/json",
      },
      body: body.toString(),
      credentials: "same-origin",
      redirect: "follow",
    }).then(function (r) {
      var ct = (r.headers.get("content-type") || "").toLowerCase();
      if (ct.indexOf("application/json") !== -1) {
        return r.json().then(function (data) {
          return { status: r.status, data: data, url: r.url };
        });
      }
      return { status: r.status, data: null, url: r.url };
    });
  }

  function clientValidateLogin(form) {
    clearFormErrors(form);
    var phoneEl = document.getElementById("login-phone") || form.querySelector('[name="phone"]');
    var passEl = document.getElementById("login-pass") || form.querySelector('[name="password"]');
    var phone = ((phoneEl && phoneEl.value) || "").trim();
    var password = (passEl && passEl.value) || "";
    var ok = true;
    if (!phone) {
      showFieldError(form, "phone", "شماره موبایل را وارد کنید");
      ok = false;
    } else if (!validPhone(phone)) {
      showFieldError(form, "phone", "شماره باید مثل ۰۹۱۲۱۲۳۴۵۶۷ باشد");
      ok = false;
    }
    if (!password) {
      showFieldError(form, "password", "رمز عبور را وارد کنید");
      ok = false;
    } else if (password.length < 6) {
      showFieldError(form, "password", "رمز عبور باید حداقل ۶ کاراکتر باشد");
      ok = false;
    }
    if (!ok) {
      showBanner(form, "لطفاً فیلدهای مشخص‌شده را کامل کنید");
    }
    return ok ? { phone: phone, password: password } : null;
  }

  function clientValidateSignup(form) {
    clearFormErrors(form);
    var name = ((document.getElementById("signup-name") || {}).value || "").trim();
    var phone = ((document.getElementById("signup-phone") || {}).value || "").trim();
    var city = ((document.getElementById("signup-city") || {}).value || "").trim();
    var postal = ((document.getElementById("signup-postal") || {}).value || "").trim();
    var address = ((document.getElementById("signup-location") || {}).value || "").trim();
    var password = (document.getElementById("signup-pass") || {}).value || "";
    var ok = true;
    if (!name) {
      showFieldError(form, "full_name", "نام و نام خانوادگی الزامی است");
      ok = false;
    }
    if (!validPhone(phone)) {
      showFieldError(form, "phone", "شماره باید مثل ۰۹۱۲۱۲۳۴۵۶۷ باشد");
      ok = false;
    }
    if (!city) {
      showFieldError(form, "city", "شهر را وارد کنید");
      ok = false;
    }
    if (postal && !/^\d{10}$/.test(postal)) {
      showFieldError(form, "postal_code", "کد پستی باید ۱۰ رقم باشد");
      ok = false;
    }
    if (!address) {
      showFieldError(form, "address", "آدرس را وارد کنید");
      ok = false;
    }
    if (!password) {
      showFieldError(form, "password", "رمز عبور را وارد کنید");
      ok = false;
    } else if (password.length < 6) {
      showFieldError(form, "password", "رمز عبور باید حداقل ۶ کاراکتر باشد");
      ok = false;
    }
    if (!ok) {
      showBanner(form, "لطفاً فیلدهای مشخص‌شده را کامل کنید");
    }
    return ok
      ? {
          full_name: name,
          phone: phone,
          city: city,
          postal_code: postal,
          address: address,
          password: password,
        }
      : null;
  }

  function handleAuthResult(form, res, failMsg) {
    if (res.data && res.data.ok === true) {
      window.location.href = res.data.redirect || "/auth/go/";
      return;
    }
    if (res.data && res.data.ok === false) {
      showErrors(form, res.data);
      return;
    }
    // HTML redirect follow: landed on panel URL after success
    if (res.url && (res.url.indexOf("/user/") !== -1 || res.url.indexOf("/staff/") !== -1 || res.url.indexOf("/auth/go") !== -1)) {
      window.location.href = "/auth/go/";
      return;
    }
    showErrors(form, { message: failMsg });
  }

  document.addEventListener(
    "submit",
    function (e) {
      if (e.target.id !== "form-login" && e.target.id !== "form-signup") return;
      e.preventDefault();
      e.stopImmediatePropagation();

      var form = e.target;
      ensureErrorUi(form);
      var btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.classList.add("is-busy");
      }

      if (form.id === "form-login") {
        var loginData = clientValidateLogin(form);
        if (!loginData) {
          if (btn) {
            btn.disabled = false;
            btn.classList.remove("is-busy");
          }
          return;
        }
        postAuth("/auth/login/", loginData)
          .then(function (res) {
            handleAuthResult(form, res, "شماره یا رمز عبور اشتباه است");
          })
          .catch(function () {
            showErrors(form, { message: "ارتباط برقرار نشد — دوباره تلاش کنید" });
          })
          .finally(function () {
            if (btn) {
              btn.disabled = false;
              btn.classList.remove("is-busy");
            }
          });
        return;
      }

      var signupData = clientValidateSignup(form);
      if (!signupData) {
        if (btn) {
          btn.disabled = false;
          btn.classList.remove("is-busy");
        }
        return;
      }
      postAuth("/auth/signup/", signupData)
        .then(function (res) {
          handleAuthResult(form, res, "ثبت‌نام انجام نشد — اطلاعات را بررسی کنید");
        })
        .catch(function () {
          showErrors(form, { message: "ارتباط برقرار نشد — دوباره تلاش کنید" });
        })
        .finally(function () {
          if (btn) {
            btn.disabled = false;
            btn.classList.remove("is-busy");
          }
        });
    },
    true
  );
})();
