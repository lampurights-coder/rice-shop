(function () {
  "use strict";

  function csrfToken() {
    var input = document.querySelector("[name=csrfmiddlewaretoken]");
    if (input && input.value) return input.value;
    var m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  function fa(n) {
    try {
      return Number(n).toLocaleString("fa-IR");
    } catch (e) {
      return String(n);
    }
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function showToast(msg) {
    var el = document.getElementById("pd-toast") || document.getElementById("toast") || document.getElementById("cart-toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "cart-toast";
      el.className = "cart-toast";
      document.body.appendChild(el);
    }
    el.hidden = false;
    el.textContent = msg;
    clearTimeout(el._t);
    el._t = setTimeout(function () {
      el.hidden = true;
    }, 2200);
  }

  function updateCartBadge(count) {
    var badge = document.getElementById("cart-badge");
    if (!badge) return;
    if (count > 0) {
      badge.hidden = false;
      badge.textContent = fa(count);
    } else {
      badge.hidden = true;
    }
  }

  /* -------- Products catalog (filters without full reload) -------- */
  function initCatalog() {
    var form = document.getElementById("shop-filters");
    var grid = document.getElementById("product-grid");
    if (!form || !grid) return;

    var processInput = document.getElementById("filter-process");
    var qualityInput = document.getElementById("filter-quality");
    var qInput = document.getElementById("catalog-q");
    var sortEl = form.querySelector('select[name="sort"]');
    var countEl = document.querySelector(".catalog-count");
    var wrap = document.querySelector(".table-wrap");
    var timer = null;
    var reqId = 0;

    function params() {
      var p = new URLSearchParams();
      var q = (qInput && qInput.value.trim()) || "";
      var process = (processInput && processInput.value) || "all";
      var quality = (qualityInput && qualityInput.value) || "all";
      var sort = (sortEl && sortEl.value) || "featured";
      if (q) p.set("q", q);
      if (process && process !== "all") p.set("process", process);
      if (quality && quality !== "all") p.set("quality", quality);
      if (sort && sort !== "featured") p.set("sort", sort);
      return p;
    }

    function setChipState(rootId, attr, value) {
      var root = document.getElementById(rootId);
      if (!root) return;
      root.querySelectorAll("button[" + attr + "]").forEach(function (btn) {
        btn.classList.toggle("is-on", btn.getAttribute(attr) === value);
      });
    }

    function rowHtml(item) {
      return (
        "<tr>" +
        '<td class="col-name"><img src="' +
        esc(item.image || "") +
        '" alt="" /><div><strong>' +
        esc(item.name) +
        "</strong>" +
        (item.featured ? ' <span class="sale-tag">پرفروش</span>' : "") +
        "</div></td>" +
        '<td><span class="sieve">' +
        esc(item.process) +
        "</span></td>" +
        "<td>" +
        esc(item.quality) +
        "<br />" +
        (item.has_reviews
          ? '<span class="stars">' +
            item.stars_html +
            '</span> <small class="rating-avg">(' +
            esc(item.avg_text) +
            ")</small>"
          : '<span class="rating-empty">بدون نظر</span>') +
        "</td>" +
        '<td class="price">' +
        esc(item.wholesale_text) +
        "</td>" +
        '<td class="price">' +
        esc(item.retail_text) +
        "</td>" +
        '<td class="col-actions"><a class="product-buy view-btn" href="' +
        esc(item.url) +
        '">مشاهده محصول</a></td>' +
        "</tr>"
      );
    }

    function render(data) {
      var q = data.q || "";
      if (!data.products || !data.products.length) {
        grid.innerHTML =
          '<tr><td colspan="6" class="catalog-empty">' +
          (q
            ? "نتیجه‌ای برای «" + q + "» پیدا نشد. واژه دیگری مثل «هاشمی» یا «ممتاز» را امتحان کنید."
            : "محصولی یافت نشد.") +
          "</td></tr>";
      } else {
        grid.innerHTML = data.products.map(rowHtml).join("");
      }
      if (countEl) {
        countEl.textContent =
          (q ? "نتایج «" + q + "»: " : "") + "تعداد محصولات: " + (data.count_text || fa(data.count)) + " مورد";
      }
      setChipState("process-filters", "data-process", data.process || "all");
      setChipState("quality-filters", "data-quality", data.quality || "all");
      if (sortEl && data.sort) sortEl.value = data.sort;
    }

    function load(push) {
      var p = params();
      var id = ++reqId;
      if (wrap) wrap.classList.add("is-loading");
      fetch("/products/?" + p.toString(), {
        headers: { Accept: "application/json", "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin",
      })
        .then(function (r) {
          return r.json();
        })
        .then(function (data) {
          if (id !== reqId) return;
          render(data);
          var url = "/products/" + (p.toString() ? "?" + p.toString() : "");
          if (push !== false) history.replaceState({ soft: true }, "", url);
        })
        .catch(function () {
          showToast("خطا در بارگذاری فهرست");
        })
        .finally(function () {
          if (wrap) wrap.classList.remove("is-loading");
        });
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      load(true);
    });

    if (sortEl) {
      sortEl.removeAttribute("onchange");
      sortEl.addEventListener("change", function () {
        load(true);
      });
    }

    if (qInput) {
      qInput.addEventListener("input", function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
          load(true);
        }, 280);
      });
    }

    function bindChips(rootId, attr, hidden) {
      var root = document.getElementById(rootId);
      if (!root || !hidden) return;
      root.addEventListener("click", function (e) {
        var btn = e.target.closest("button[" + attr + "]");
        if (!btn) return;
        hidden.value = btn.getAttribute(attr);
        load(true);
      });
    }
    bindChips("process-filters", "data-process", processInput);
    bindChips("quality-filters", "data-quality", qualityInput);

    var clear = document.querySelector(".clear-filters");
    if (clear) {
      clear.addEventListener("click", function (e) {
        e.preventDefault();
        if (qInput) qInput.value = "";
        if (processInput) processInput.value = "all";
        if (qualityInput) qualityInput.value = "all";
        if (sortEl) sortEl.value = "featured";
        load(true);
      });
    }

    window.addEventListener("popstate", function () {
      var sp = new URLSearchParams(window.location.search);
      if (qInput) qInput.value = sp.get("q") || "";
      if (processInput) processInput.value = sp.get("process") || "all";
      if (qualityInput) qualityInput.value = sp.get("quality") || "all";
      if (sortEl) sortEl.value = sp.get("sort") || "featured";
      load(false);
    });
  }

  /* -------- Reviews without full reload -------- */
  function initReviews() {
    var form = document.getElementById("review-form");
    var list = document.getElementById("reviews-list");
    if (!form || !list) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      if (btn) btn.disabled = true;
      var body = new URLSearchParams(new FormData(form));
      fetch(form.action, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          Accept: "application/json",
          "X-CSRFToken": csrfToken(),
        },
        body: body.toString(),
        credentials: "same-origin",
      })
        .then(function (r) {
          return r.json().then(function (data) {
            return { ok: r.ok, data: data };
          });
        })
        .then(function (res) {
          if (!res.data || !res.data.ok) {
            showToast((res.data && res.data.message) || "نظر ثبت نشد");
            return;
          }
          var r = res.data.review;
          var empty = list.querySelector(".pd-reviews-based");
          if (empty && !list.querySelector(".pd-review")) empty.remove();
          var article = document.createElement("article");
          article.className = "pd-review is-new";
          article.innerHTML =
            '<div class="pd-review-meta"><div class="pd-review-who"><strong>' +
            esc(r.author_name) +
            "</strong>" +
            (r.verified ? '<span class="pd-review-verified">خریدار تأییدشده</span>' : "") +
            '</div><span class="pd-review-date">' +
            esc(r.date) +
            "</span></div>" +
            '<div class="pd-review-title-row"><span class="pd-review-stars" aria-hidden="true">' +
            esc(r.stars_glyphs) +
            '</span><span class="pd-review-title">' +
            esc(r.title) +
            "</span></div>" +
            '<p class="pd-review-body">' +
            esc(r.body) +
            "</p>" +
            '<p class="pd-review-product">' +
            esc(r.product_label) +
            "</p>";
          list.insertBefore(article, list.firstChild);

          var stats = res.data.stats || {};
          var score = document.getElementById("reviews-score");
          var stars = document.getElementById("reviews-stars");
          var based = document.getElementById("reviews-based");
          var emptyBox = document.getElementById("reviews-summary-empty");
          if (emptyBox && stats.count) {
            emptyBox.removeAttribute("id");
            emptyBox.innerHTML =
              '<div class="pd-reviews-score" id="reviews-score"></div><div><div class="pd-reviews-stars" id="reviews-stars" aria-hidden="true"></div><p class="pd-reviews-based" id="reviews-based"></p></div>';
            score = document.getElementById("reviews-score");
            stars = document.getElementById("reviews-stars");
            based = document.getElementById("reviews-based");
          }
          if (score) {
            score.hidden = false;
            score.textContent = stats.avg_text || score.textContent;
          }
          if (stars) {
            stars.hidden = false;
            stars.textContent = stats.stars || stars.textContent;
          }
          if (based) {
            based.textContent = stats.count
              ? "بر اساس " + (stats.count_text || fa(stats.count)) + " نظر"
              : based.textContent;
          }
          var rating = document.getElementById("pd-rating");
          if (!rating && stats.count) {
            var title = document.getElementById("product-title");
            if (title) {
              rating = document.createElement("div");
              rating.className = "pd-rating";
              rating.id = "pd-rating";
              rating.innerHTML =
                '<span class="pd-stars" aria-hidden="true">' +
                esc(stats.stars || "") +
                "</span><span>(" +
                esc(stats.avg_text || "") +
                ") " +
                esc(stats.count_text || fa(stats.count)) +
                " نظر</span>";
              title.insertAdjacentElement("afterend", rating);
            }
          } else if (rating && stats.count) {
            var starEl = rating.querySelector(".pd-stars");
            var textEl = rating.querySelector("span:last-child");
            if (starEl) starEl.textContent = stats.stars || "";
            if (textEl) {
              textEl.textContent =
                "(" + (stats.avg_text || "") + ") " + (stats.count_text || fa(stats.count)) + " نظر";
            }
          }
          form.reset();
          form.hidden = true;
          showToast(res.data.message || "نظر شما ثبت شد");
          article.scrollIntoView({ behavior: "smooth", block: "nearest" });
        })
        .catch(function () {
          showToast("خطا در ارسال نظر");
        })
        .finally(function () {
          if (btn) btn.disabled = false;
        });
    });
  }

  /* -------- Add to cart without leaving product page -------- */
  function initCartAdd() {
    var form = document.getElementById("add-cart-form");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      if (btn) btn.disabled = true;
      var body = new URLSearchParams(new FormData(form));
      fetch(form.action, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          Accept: "application/json",
          "X-CSRFToken": csrfToken(),
        },
        body: body.toString(),
        credentials: "same-origin",
      })
        .then(function (r) {
          return r.json().then(function (data) {
            return { status: r.status, data: data };
          });
        })
        .then(function (res) {
          if (res.status === 403) {
            showToast((res.data && res.data.message) || "برای خرید با حساب مشتری وارد شوید");
            return;
          }
          if (!res.data || !res.data.ok) {
            showToast((res.data && res.data.message) || "افزودن به سبد انجام نشد");
            return;
          }
          updateCartBadge(res.data.cart_count || 0);
          showToast(res.data.message || "به سبد اضافه شد");
        })
        .catch(function () {
          showToast("خطا در افزودن به سبد");
        })
        .finally(function () {
          if (btn) btn.disabled = false;
        });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initCatalog();
    initReviews();
    initCartAdd();
  });
})();
