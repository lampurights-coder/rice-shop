(function () {
  "use strict";

  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* Mobile nav */
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("main-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "بستن منو" : "باز کردن منو");
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* Active nav on scroll */
  var sections = ["home", "products", "about", "blog"]
    .map(function (id) {
      return document.getElementById(id);
    })
    .filter(Boolean);

  function updateActiveNav() {
    var y = window.scrollY + 120;
    var current = sections[0] && sections[0].id;
    sections.forEach(function (sec) {
      if (sec.offsetTop <= y) current = sec.id;
    });
    document.querySelectorAll(".nav-link").forEach(function (link) {
      var href = link.getAttribute("href") || "";
      link.classList.toggle("is-active", href === "#" + current);
    });
  }

  window.addEventListener("scroll", updateActiveNav, { passive: true });
  updateActiveNav();

  /* Scroll reveal */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.18, rootMargin: "0px 0px -40px 0px" }
    );
    reveals.forEach(function (el) {
      io.observe(el);
    });
  } else {
    reveals.forEach(function (el) {
      el.classList.add("is-visible");
    });
  }

  /* Animated counters */
  function animateValue(el, end, suffix, duration) {
    var start = 0;
    var startTime = null;
    suffix = suffix || "";

    function frame(ts) {
      if (!startTime) startTime = ts;
      var progress = Math.min((ts - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var value = Math.round(start + (end - start) * eased);
      el.textContent = value + suffix;
      if (progress < 1) requestAnimationFrame(frame);
    }

    requestAnimationFrame(frame);
  }

  var statsRoot = document.querySelector(".hero-stats");
  var counted = false;

  function runCounters() {
    if (counted) return;
    counted = true;
    document.querySelectorAll(".stat-value[data-count]").forEach(function (el) {
      var end = parseInt(el.getAttribute("data-count"), 10) || 0;
      var suffix = el.getAttribute("data-suffix") || "";
      animateValue(el, end, suffix, 1200);
    });
  }

  if (statsRoot && "IntersectionObserver" in window) {
    var statsIo = new IntersectionObserver(
      function (entries) {
        if (entries.some(function (e) {
          return e.isIntersecting;
        })) {
          runCounters();
          statsIo.disconnect();
        }
      },
      { threshold: 0.4 }
    );
    statsIo.observe(statsRoot);
  } else {
    runCounters();
  }

  /* Video modal */
  var modal = document.getElementById("video-modal");
  var openBtn = document.getElementById("video-open");

  function openModal() {
    if (!modal) return;
    modal.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    if (!modal) return;
    modal.hidden = true;
    document.body.style.overflow = "";
  }

  if (openBtn) openBtn.addEventListener("click", openModal);
  if (modal) {
    modal.querySelectorAll("[data-close]").forEach(function (el) {
      el.addEventListener("click", closeModal);
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeModal();
  });

  /* Soft parallax on hero photo */
  var photo = document.querySelector(".hero-photo");
  if (photo && window.matchMedia("(pointer: fine)").matches) {
    var hero = document.querySelector(".hero");
    hero.addEventListener(
      "mousemove",
      function (e) {
        var rect = hero.getBoundingClientRect();
        var x = (e.clientX - rect.left) / rect.width - 0.5;
        var y = (e.clientY - rect.top) / rect.height - 0.5;
        photo.style.transform =
          "translate(" + x * 8 + "px, " + y * 6 + "px) scale(1.02)";
      },
      { passive: true }
    );
    hero.addEventListener("mouseleave", function () {
      photo.style.transform = "";
    });
  }

  var toast = document.getElementById("cart-toast");
  var toastTimer = null;
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest(".product-buy");
    if (!btn || !toast) return;
    if (btn.classList.contains("view-btn") || btn.tagName === "A") return;
    var name = btn.getAttribute("data-product") || "محصول";
    toast.textContent = name + " به سبد خرید اضافه شد";
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toast.hidden = true;
    }, 2200);
  });

  /* Cart drawer + header tools */
  (function initCartDrawer() {
    var FREE_SHIP = 2000000;
    var suggestions = [
      { name: "صدری دم سیاه آستانه", price: 680000 },
      { name: "طارم هاشمی ممتاز", price: 480000 },
      { name: "برنج قهوه‌ای فوق ممتاز", price: 548000 }
    ];

    if (!document.getElementById("cart-drawer")) {
      var wrap = document.createElement("div");
      wrap.innerHTML =
        '<div class="cart-backdrop" id="cart-backdrop" hidden></div>' +
        '<aside class="cart-drawer" id="cart-drawer" aria-hidden="true" role="dialog" aria-labelledby="cart-title">' +
        '<div class="cart-drawer-head"><h2 id="cart-title">سبد خرید شما</h2>' +
        '<button type="button" class="cart-close" id="cart-close" aria-label="بستن">×</button></div>' +
        '<div class="cart-banner">تخفیف‌ها در مرحله پرداخت اعمال می‌شوند. ارسال رایگان برای سفارش‌های بالای ۲ میلیون تومان.</div>' +
        '<div class="cart-ship"><div class="cart-ship-bar"><div class="cart-ship-fill" id="cart-ship-fill"></div></div>' +
        '<p id="cart-ship-text"></p></div>' +
        '<div class="cart-body">' +
        '<div class="cart-empty" id="cart-empty"><p>سبد خرید خالی است! محصولات موردعلاقه‌تان را اضافه کنید.</p>' +
        '<a class="cart-cta" href="/products/">مشاهده فروشگاه</a></div>' +
        '<div class="cart-suggest"><h3>شاید بپسندید</h3><div id="cart-suggest-list"></div></div>' +
        "</div></aside>" +
        '<div class="nav-search-panel" id="nav-search-panel">' +
        '<div class="nav-search-row">' +
        '<input type="search" id="nav-search-input" placeholder="جستجوی برنج..." autocomplete="off" />' +
        "</div>" +
        '<div class="nav-search-results" id="nav-search-results" hidden></div>' +
        "</div>";
      document.body.appendChild(wrap);
    }

    var drawer = document.getElementById("cart-drawer");
    var backdrop = document.getElementById("cart-backdrop");
    var openBtn = document.getElementById("nav-cart-btn");
    var closeBtn = document.getElementById("cart-close");
    var shipFill = document.getElementById("cart-ship-fill");
    var shipText = document.getElementById("cart-ship-text");
    var suggestList = document.getElementById("cart-suggest-list");
    var searchBtn = document.getElementById("nav-search-btn");
    var searchPanel = document.getElementById("nav-search-panel");
    var searchInput = document.getElementById("nav-search-input");

    function money(n) {
      return n.toLocaleString("fa-IR");
    }

    function updateShip(total) {
      var remain = Math.max(0, FREE_SHIP - total);
      var pct = Math.min(100, (total / FREE_SHIP) * 100);
      if (shipFill) shipFill.style.width = pct + "%";
      if (shipText) {
        shipText.innerHTML =
          remain === 0
            ? "ارسال این سفارش <strong>رایگان</strong> است!"
            : money(remain) + " تومان تا <strong>ارسال رایگان</strong> فاصله دارید";
      }
    }

    if (suggestList) {
      suggestList.innerHTML = suggestions
        .map(function (item, i) {
          return (
            '<div class="cart-suggest-item"><div><strong>' +
            item.name +
            "</strong><span>" +
            money(item.price) +
            ' تومان</span></div><button type="button" class="cart-add" data-suggest="' +
            i +
            '">افزودن</button></div>'
          );
        })
        .join("");
    }

    updateShip(0);

    function openCart() {
      if (!drawer || !backdrop) return;
      backdrop.hidden = false;
      requestAnimationFrame(function () {
        backdrop.classList.add("is-open");
        drawer.classList.add("is-open");
      });
      drawer.setAttribute("aria-hidden", "false");
      if (openBtn) openBtn.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden";
    }

    function closeCart() {
      if (!drawer || !backdrop) return;
      backdrop.classList.remove("is-open");
      drawer.classList.remove("is-open");
      drawer.setAttribute("aria-hidden", "true");
      if (openBtn) openBtn.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
      setTimeout(function () {
        if (!drawer.classList.contains("is-open")) backdrop.hidden = true;
      }, 300);
    }

    if (openBtn) {
      openBtn.addEventListener("click", function (e) {
        var href = openBtn.getAttribute("href") || "";
        // Real cart / auth links navigate; only open demo drawer for bare #
        if (openBtn.hasAttribute("data-auth-open")) return;
        if (href && href !== "#") return;
        e.preventDefault();
        openCart();
      });
    }
    if (closeBtn) closeBtn.addEventListener("click", closeCart);
    if (backdrop) backdrop.addEventListener("click", closeCart);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        closeCart();
        if (searchPanel) searchPanel.classList.remove("is-open");
      }
    });

    if (suggestList) {
      suggestList.addEventListener("click", function (e) {
        var add = e.target.closest(".cart-add");
        if (!add) return;
        var idx = parseInt(add.getAttribute("data-suggest"), 10);
        var item = suggestions[idx];
        if (!item) return;
        updateShip(item.price);
        var badge = document.getElementById("cart-badge");
        if (badge) {
          badge.hidden = false;
          badge.textContent = "۱";
        }
        var empty = document.getElementById("cart-empty");
        if (empty) {
          empty.innerHTML =
            '<p style="text-align:right;margin:0 0 12px"><strong>' +
            item.name +
            "</strong><br/><span>" +
            money(item.price) +
            " تومان × ۱</span></p>" +
            '<a class="cart-cta" href="/products/">ادامه خرید</a>';
        }
      });
    }

    if (searchBtn && searchPanel && searchInput) {
      var resultsEl = document.getElementById("nav-search-results");
      if (!resultsEl) {
        resultsEl = document.createElement("div");
        resultsEl.id = "nav-search-results";
        resultsEl.className = "nav-search-results";
        resultsEl.hidden = true;
        searchPanel.appendChild(resultsEl);
      }
      searchPanel.querySelectorAll(".nav-search-go").forEach(function (btn) {
        btn.remove();
      });
      var searchTimer = null;
      var activeIdx = -1;
      var lastResults = [];

      function moneyFa(n) {
        try {
          return Number(n).toLocaleString("fa-IR") + " تومان";
        } catch (err) {
          return n + " تومان";
        }
      }

      function renderResults(items, q) {
        lastResults = items || [];
        activeIdx = -1;
        if (!q) {
          resultsEl.hidden = true;
          resultsEl.innerHTML = "";
          return;
        }
        if (!lastResults.length) {
          resultsEl.hidden = false;
          resultsEl.innerHTML =
            '<p class="nav-search-empty">نتیجه‌ای برای «' +
            q.replace(/</g, "&lt;") +
            "» پیدا نشد</p>";
          return;
        }
        resultsEl.hidden = false;
        resultsEl.innerHTML =
          '<p class="nav-search-hint">بهترین تطبیق‌ها</p>' +
          lastResults
            .map(function (item, i) {
              return (
                '<a class="nav-search-item" href="' +
                item.url +
                '" data-idx="' +
                i +
                '">' +
                (item.image
                  ? '<img src="' + item.image + '" alt="" />'
                  : '<span class="nav-search-thumb" aria-hidden="true"></span>') +
                '<span class="nav-search-meta"><strong>' +
                item.name +
                "</strong><small>" +
                (item.quality || item.process || "") +
                " · " +
                moneyFa(item.price) +
                "</small></span>" +
                (item.featured ? '<span class="nav-search-badge">پرفروش</span>' : "") +
                "</a>"
              );
            })
            .join("") +
          '<a class="nav-search-all" href="/products/?q=' +
          encodeURIComponent(q) +
          '">مشاهده همه نتایج ←</a>';
      }

      function fetchMatches(q) {
        if (!q) {
          renderResults([], "");
          return;
        }
        resultsEl.hidden = false;
        resultsEl.innerHTML = '<p class="nav-search-empty">در حال جستجو…</p>';
        fetch("/api/products/search/?q=" + encodeURIComponent(q) + "&limit=6", {
          headers: { Accept: "application/json" },
          credentials: "same-origin",
        })
          .then(function (r) {
            return r.json();
          })
          .then(function (data) {
            if (searchInput.value.trim() !== q) return;
            renderResults((data && data.results) || [], q);
          })
          .catch(function () {
            resultsEl.innerHTML = '<p class="nav-search-empty">خطا در جستجو</p>';
          });
      }

      function highlightActive() {
        resultsEl.querySelectorAll(".nav-search-item").forEach(function (el, i) {
          el.classList.toggle("is-active", i === activeIdx);
        });
      }

      searchBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        var header = document.querySelector(".site-header");
        if (header && searchPanel.parentElement !== header) {
          header.appendChild(searchPanel);
        }
        searchPanel.classList.toggle("is-open");
        if (searchPanel.classList.contains("is-open")) {
          searchInput.focus();
          var q = searchInput.value.trim();
          if (q) fetchMatches(q);
        }
      });

      searchInput.addEventListener("input", function () {
        var q = searchInput.value.trim();
        clearTimeout(searchTimer);
        searchTimer = setTimeout(function () {
          fetchMatches(q);
        }, 180);
      });

      searchInput.addEventListener("keydown", function (e) {
        var items = resultsEl.querySelectorAll(".nav-search-item");
        if (e.key === "ArrowDown" && items.length) {
          e.preventDefault();
          activeIdx = (activeIdx + 1) % items.length;
          highlightActive();
          return;
        }
        if (e.key === "ArrowUp" && items.length) {
          e.preventDefault();
          activeIdx = activeIdx <= 0 ? items.length - 1 : activeIdx - 1;
          highlightActive();
          return;
        }
        if (e.key === "Enter") {
          e.preventDefault();
          // Stay on page unless a match is chosen: open best match
          if (activeIdx >= 0 && items[activeIdx]) {
            window.location.href = items[activeIdx].getAttribute("href");
            return;
          }
          if (lastResults.length && lastResults[0].url) {
            window.location.href = lastResults[0].url;
            return;
          }
          fetchMatches(searchInput.value.trim());
        }
      });

      document.addEventListener("click", function (e) {
        if (!searchPanel.classList.contains("is-open")) return;
        if (e.target.closest("#nav-search-panel") || e.target.closest("#nav-search-btn")) return;
        searchPanel.classList.remove("is-open");
      });
    }
  })();
})();
