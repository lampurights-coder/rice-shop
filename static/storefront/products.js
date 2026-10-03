(function () {
  "use strict";

  var grid = document.getElementById("product-grid");
  if (!grid) return;

  var PAGE_SIZE = 6;
  var PRODUCTS = [
    { name: "صدری دم سیاه آستانه اشرفیه", process: "یک بار الک", quality: "برنج فوق ممتاز", stars: 5, wholesale: 590000, retail: 680000, featured: true, deal: true, oldRetail: 790000 },
    { name: "برنج امراللهی کشت دوم", process: "یک بار الک", quality: "برنج فوق ممتاز", stars: 5, wholesale: 480000, retail: 575000, featured: true, deal: true, oldRetail: 690000 },
    { name: "برنج قهوه‌ای فوق ممتاز", process: "دوبار الک", quality: "برنج فوق ممتاز", stars: 4, wholesale: 475000, retail: 548000, featured: false },
    { name: "برنج طارم هاشمی ممتاز", process: "یک بار الک", quality: "برنج ممتاز", stars: 4, wholesale: 403000, retail: 480000, featured: true, deal: true, oldRetail: 555000 },
    { name: "برنج فجر گرگان", process: "یک بار الک", quality: "اقتصادی", stars: 3, wholesale: 335000, retail: 410000, featured: false },
    { name: "صدری هاشمی ممتاز ۵ کیلویی", process: "دوبار الک", quality: "برنج فوق ممتاز", stars: 5, wholesale: 620000, retail: 720000, featured: true, deal: true, oldRetail: 860000 },
    { name: "صدری دمسیاه فوق ممتاز ۱۰ کیلویی", process: "یک بار الک", quality: "برنج فوق ممتاز", stars: 5, wholesale: 560000, retail: 648000, featured: true, deal: true, oldRetail: 740000 },
    { name: "برنج هاشمی کشت دوم", process: "دوبار الک", quality: "برنج ممتاز", stars: 4, wholesale: 390000, retail: 465000, featured: false },
    { name: "برنج عنبربو خوزستان", process: "یک بار الک", quality: "برنج ممتاز", stars: 4, wholesale: 510000, retail: 595000, featured: false },
    { name: "برنج طارم محلی", process: "دوبار الک", quality: "برنج فوق ممتاز", stars: 5, wholesale: 530000, retail: 610000, featured: true },
    { name: "برنج اقتصادی خانواده", process: "یک بار الک", quality: "اقتصادی", stars: 3, wholesale: 280000, retail: 345000, featured: false },
    { name: "برنج صدری گیلان", process: "دوبار الک", quality: "برنج ممتاز", stars: 4, wholesale: 450000, retail: 530000, featured: false }
  ];

  var state = { q: "", process: "all", quality: "all", sort: "featured", page: 1 };

  var searchEl = document.getElementById("product-search");
  var sortEl = document.getElementById("product-sort");
  var countEl = document.getElementById("product-count");
  var emptyEl = document.getElementById("product-empty");
  var pagerEl = document.getElementById("product-pager");
  var dealEl = document.getElementById("deal-list");

  function money(n) {
    return n.toLocaleString("fa-IR");
  }

  function stars(n) {
    var html = "";
    for (var i = 1; i <= 5; i++) html += '<span class="' + (i <= n ? "is-on" : "") + '">★</span>';
    return '<span class="stars" aria-label="' + n + ' از ۵">' + html + "</span>";
  }

  function filtered() {
    var list = PRODUCTS.filter(function (item) {
      var q = state.q.trim();
      var matchesQ = !q || item.name.indexOf(q) !== -1;
      var matchesProcess = state.process === "all" || item.process === state.process;
      var matchesQuality = state.quality === "all" || item.quality === state.quality;
      return matchesQ && matchesProcess && matchesQuality;
    });
    list.sort(function (a, b) {
      if (state.sort === "price-asc") return a.retail - b.retail;
      if (state.sort === "price-desc") return b.retail - a.retail;
      if (state.sort === "name") return a.name.localeCompare(b.name, "fa");
      return Number(b.featured) - Number(a.featured);
    });
    return list;
  }

  function productIndex(item) {
    for (var i = 0; i < PRODUCTS.length; i++) {
      if (PRODUCTS[i].name === item.name) return i;
    }
    return 0;
  }

  function row(item) {
    var badge = item.featured ? '<span class="sale-tag">پرفروش</span>' : "";
    var idx = productIndex(item);
    return (
      "<tr>" +
      '<td class="col-name"><img src="../berenj.webp" alt="" /><div><strong>' +
      item.name +
      "</strong>" +
      badge +
      "</div></td>" +
      '<td><span class="sieve">' +
      item.process +
      "</span></td>" +
      "<td>" +
      item.quality +
      "<br />" +
      stars(item.stars) +
      "</td>" +
      '<td class="price">' +
      money(item.wholesale) +
      "<small>تومان</small></td>" +
      '<td class="price">' +
      money(item.retail) +
      "<small>تومان</small></td>" +
      '<td class="col-actions">' +
      '<a class="product-buy view-btn" href="product-detail.html?p=' +
      idx +
      '">مشاهده محصول</a>' +
      '<button class="fav-btn" type="button">افزودن به علاقه‌مندی</button>' +
      "</td>" +
      "</tr>"
    );
  }

  function dealCard(item) {
    return (
      '<article class="deal-card">' +
      "<div><strong>" +
      item.name +
      "</strong>" +
      stars(item.stars) +
      '<div class="deal-prices"><s>' +
      money(item.oldRetail) +
      "</s><b>" +
      money(item.retail) +
      " تومان</b></div></div>" +
      '<img src="../berenj.webp" alt="" />' +
      "</article>"
    );
  }

  function renderDeals() {
    dealEl.innerHTML = PRODUCTS.filter(function (item) {
      return item.deal;
    })
      .map(dealCard)
      .join("");
  }

  function render() {
    var list = filtered();
    var pages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
    if (state.page > pages) state.page = pages;
    var start = (state.page - 1) * PAGE_SIZE;
    var slice = list.slice(start, start + PAGE_SIZE);
    grid.innerHTML = slice.map(row).join("");
    emptyEl.hidden = slice.length !== 0;
    countEl.textContent = "تعداد محصولات: " + list.length.toLocaleString("fa-IR") + " مورد";

    var html = '<button type="button" data-page="prev"' + (state.page === 1 ? " disabled" : "") + ">قبلی</button>";
    for (var i = 1; i <= pages; i++) {
      html += '<button type="button" data-page="' + i + '"' + (i === state.page ? ' class="is-on"' : "") + ">" + i.toLocaleString("fa-IR") + "</button>";
    }
    html += '<button type="button" data-page="next"' + (state.page === pages ? " disabled" : "") + ">بعدی</button>";
    pagerEl.innerHTML = list.length > PAGE_SIZE ? html : "";
  }

  function setChips(root, attr, value) {
    root.querySelectorAll("button").forEach(function (chip) {
      chip.classList.toggle("is-on", chip.getAttribute(attr) === value);
    });
  }

  searchEl.addEventListener("input", function () {
    state.q = searchEl.value;
    state.page = 1;
    render();
  });
  sortEl.addEventListener("change", function () {
    state.sort = sortEl.value;
    state.page = 1;
    render();
  });
  document.getElementById("process-filters").addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-process]");
    if (!btn) return;
    state.process = btn.getAttribute("data-process");
    state.page = 1;
    setChips(e.currentTarget, "data-process", state.process);
    render();
  });
  document.getElementById("quality-filters").addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-quality]");
    if (!btn) return;
    state.quality = btn.getAttribute("data-quality");
    state.page = 1;
    setChips(e.currentTarget, "data-quality", state.quality);
    render();
  });
  document.getElementById("clear-filters").addEventListener("click", function () {
    state.q = "";
    state.process = "all";
    state.quality = "all";
    state.sort = "featured";
    state.page = 1;
    searchEl.value = "";
    sortEl.value = "featured";
    setChips(document.getElementById("process-filters"), "data-process", "all");
    setChips(document.getElementById("quality-filters"), "data-quality", "all");
    render();
  });
  pagerEl.addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-page]");
    if (!btn || btn.disabled) return;
    var value = btn.getAttribute("data-page");
    if (value === "prev") state.page -= 1;
    else if (value === "next") state.page += 1;
    else state.page = parseInt(value, 10);
    render();
  });
  grid.addEventListener("click", function (e) {
    var fav = e.target.closest(".fav-btn");
    if (!fav) return;
    fav.classList.toggle("is-on");
    fav.textContent = fav.classList.contains("is-on") ? "در علاقه‌مندی‌ها" : "افزودن به علاقه‌مندی";
  });

  renderDeals();
  var qParam = new URLSearchParams(window.location.search).get("q");
  if (qParam) {
    searchEl.value = qParam;
    state.q = qParam;
  }
  render();
})();
