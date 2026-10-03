(function () {
  "use strict";

  var PRODUCTS = [
    {
      name: "صدری دم سیاه آستانه اشرفیه",
      process: "یک بار الک",
      quality: "برنج فوق ممتاز",
      stars: 5,
      wholesale: 590000,
      retail: 680000,
      deal: true,
      oldRetail: 790000,
      desc: "صدری دم‌سیاه آستانه با عطر دلنشین و دانه‌های بلند؛ مناسب پلوهای رسمی و مهمانی. پایه برنج مرغوب شمال، الک‌شده و آماده طبخ با طعمی که کمتر هم زدن می‌خواهد.",
      features: [
        "طعم رستورانی و عطر ماندگار!",
        "آماده طبخ در حدود ۲۰ دقیقه",
        "برنج فوق ممتاز کشت گیلان",
        "مناسب چلو و پلو ایرانی",
        "بدون مواد نگهدارنده",
        "بسته‌بندی بهداشتی و تازه"
      ]
    },
    {
      name: "برنج امراللهی کشت دوم",
      process: "یک بار الک",
      quality: "برنج فوق ممتاز",
      stars: 5,
      wholesale: 480000,
      retail: 575000,
      deal: true,
      oldRetail: 690000,
      desc: "امراللهی کشت دوم؛ دانه‌های شفاف و پخت نرم. انتخاب اقتصادی برای خانواده و رستوران با کیفیت فوق ممتاز.",
      features: [
        "عطر ملایم و پخت یکدست",
        "مناسب مصرف روزانه",
        "کشت دوم کنترل‌شده",
        "الک یک‌بار برای بافت بهتر",
        "بدون مواد نگهدارنده",
        "قیمت رقابتی عمده و خرده"
      ]
    },
    {
      name: "برنج قهوه‌ای فوق ممتاز",
      process: "دوبار الک",
      quality: "برنج فوق ممتاز",
      stars: 4,
      wholesale: 475000,
      retail: 548000,
      desc: "برنج قهوه‌ای فوق ممتاز با فیبر بیشتر و طعم مغزدار. انتخاب سالم برای رژیم غذایی متعادل و پخت‌های سبک.",
      features: [
        "فیبر و مواد مغذی بیشتر",
        "طعم مغزدار و طبیعی",
        "دوبار الک برای یکدستی",
        "مناسب سالاد و پلو قهوه‌ای",
        "بدون مواد نگهدارنده",
        "بسته‌بندی تازه"
      ]
    },
    {
      name: "برنج طارم هاشمی ممتاز",
      process: "یک بار الک",
      quality: "برنج ممتاز",
      stars: 4,
      wholesale: 403000,
      retail: 480000,
      deal: true,
      oldRetail: 555000,
      desc: "طارم هاشمی ممتاز؛ عطر کلاسیک شمال و دانه‌های کشیده. همراه همیشگی سفره ایرانی.",
      features: [
        "عطر طارم اصیل",
        "پخت نرم و دانه‌دانه‌",
        "مناسب مهمانی و روزانه",
        "برنج ممتاز شمال",
        "بدون مواد نگهدارنده",
        "کیفیت پایدار"
      ]
    },
    {
      name: "برنج فجر گرگان",
      process: "یک بار الک",
      quality: "اقتصادی",
      stars: 3,
      wholesale: 335000,
      retail: 410000,
      desc: "فجر گرگان؛ گزینه اقتصادی با پخت قابل قبول برای مصرف خانگی روزمره.",
      features: [
        "قیمت مناسب خانواده",
        "پخت سریع",
        "مناسب مصرف روزانه",
        "کیفیت اقتصادی پایدار",
        "بدون مواد نگهدارنده",
        "بسته‌بندی استاندارد"
      ]
    },
    {
      name: "صدری هاشمی ممتاز ۵ کیلویی",
      process: "دوبار الک",
      quality: "برنج فوق ممتاز",
      stars: 5,
      wholesale: 620000,
      retail: 720000,
      deal: true,
      oldRetail: 860000,
      desc: "صدری هاشمی ممتاز در بسته‌بندی ۵ کیلویی؛ دوبار الک برای دانه‌های یکدست و عطر قوی.",
      features: [
        "بسته‌بندی ۵ کیلویی",
        "دوبار الک فوق ممتاز",
        "عطر و طعم لوکس",
        "مناسب هدیه‌دهی و مهمانی",
        "بدون مواد نگهدارنده",
        "کیفیت صادراتی"
      ]
    },
    {
      name: "صدری دمسیاه فوق ممتاز ۱۰ کیلویی",
      process: "یک بار الک",
      quality: "برنج فوق ممتاز",
      stars: 5,
      wholesale: 560000,
      retail: 648000,
      deal: true,
      oldRetail: 740000,
      desc: "دم‌سیاه فوق ممتاز ۱۰ کیلویی برای عمده‌فروشی و مصرف پرتردد. صرفه‌جویی بیشتر در هر کیلو.",
      features: [
        "بسته‌بندی ۱۰ کیلویی",
        "صرفه‌جویی در خرید عمده",
        "عطر دم‌سیاه ماندگار",
        "مناسب رستوران و خانواده بزرگ",
        "بدون مواد نگهدارنده",
        "کیفیت فوق ممتاز"
      ]
    },
    {
      name: "برنج هاشمی کشت دوم",
      process: "دوبار الک",
      quality: "برنج ممتاز",
      stars: 4,
      wholesale: 390000,
      retail: 465000,
      desc: "هاشمی کشت دوم با بافت نرم و پخت یکدست؛ انتخاب هوشمند برای مصرف هفتگی.",
      features: [
        "بافت نرم پس از پخت",
        "دوبار الک",
        "قیمت متعادل",
        "مناسب پلو ایرانی",
        "بدون مواد نگهدارنده",
        "کیفیت ممتاز"
      ]
    },
    {
      name: "برنج عنبربو خوزستان",
      process: "یک بار الک",
      quality: "برنج ممتاز",
      stars: 4,
      wholesale: 510000,
      retail: 595000,
      desc: "عنبربو خوزستان با عطر خاص جنوبی؛ تجربه‌ای متفاوت برای عاشقان برنج معطر.",
      features: [
        "عطر عنبربو منحصربه‌فرد",
        "کشت خوزستان",
        "مناسب پلوهای معطر",
        "برنج ممتاز",
        "بدون مواد نگهدارنده",
        "بسته‌بندی تازه"
      ]
    },
    {
      name: "برنج طارم محلی",
      process: "دوبار الک",
      quality: "برنج فوق ممتاز",
      stars: 5,
      wholesale: 530000,
      retail: 610000,
      desc: "طارم محلی فوق ممتاز؛ انتخاب اصیل برای سفره‌ای که بوی شمال می‌دهد.",
      features: [
        "عطر محلی طارم",
        "دوبار الک فوق ممتاز",
        "دانه‌های بلند و شفاف",
        "مناسب مهمانی",
        "بدون مواد نگهدارنده",
        "کیفیت درجه یک"
      ]
    },
    {
      name: "برنج اقتصادی خانواده",
      process: "یک بار الک",
      quality: "اقتصادی",
      stars: 3,
      wholesale: 280000,
      retail: 345000,
      desc: "گزینه اقتصادی خانواده برای مصرف روزانه با تعادل خوب بین قیمت و کیفیت.",
      features: [
        "بهترین قیمت خانواده",
        "پخت ساده روزمره",
        "مناسب مصرف هفتگی",
        "کیفیت اقتصادی پایدار",
        "بدون مواد نگهدارنده",
        "بسته‌بندی استاندارد"
      ]
    },
    {
      name: "برنج صدری گیلان",
      process: "دوبار الک",
      quality: "برنج ممتاز",
      stars: 4,
      wholesale: 450000,
      retail: 530000,
      desc: "صدری گیلان با اصالت شمال؛ دوبار الک برای بافت یکدست و عطر ملایم.",
      features: [
        "اصالت کشت گیلان",
        "دوبار الک ممتاز",
        "عطر ملایم و دلپذیر",
        "مناسب پلو و چلو",
        "بدون مواد نگهدارنده",
        "کیفیت پایدار"
      ]
    }
  ];

  function money(n) {
    return n.toLocaleString("fa-IR");
  }

  function starsHtml(n) {
    var s = "";
    for (var i = 1; i <= 5; i++) s += i <= n ? "★" : "☆";
    return s;
  }

  function reviewsFor(stars) {
    var count = 12 + stars * 7;
    var score = (3.8 + stars * 0.24).toFixed(1).replace(".", "٫");
    return "(" + score + ") " + count.toLocaleString("fa-IR") + " نظر";
  }

  var params = new URLSearchParams(window.location.search);
  var idx = parseInt(params.get("p"), 10);
  if (isNaN(idx) || idx < 0 || idx >= PRODUCTS.length) {
    var byName = params.get("name");
    if (byName) {
      idx = PRODUCTS.findIndex(function (item) {
        return item.name === byName;
      });
    }
  }
  if (isNaN(idx) || idx < 0) idx = 0;

  var product = PRODUCTS[idx];

  document.title = product.name + " — برنج‌کِر";
  document.getElementById("crumb-name").textContent = product.name;
  document.getElementById("product-title").textContent = product.name;
  document.getElementById("pack-title").textContent = product.name;
  document.getElementById("product-stars").textContent = starsHtml(product.stars);
  document.getElementById("product-stars").setAttribute("aria-label", product.stars + " از ۵");
  document.getElementById("product-reviews").textContent = reviewsFor(product.stars);
  document.getElementById("product-desc").textContent = product.desc;
  document.getElementById("product-price").textContent = money(product.retail) + " تومان";
  document.getElementById("product-wholesale").textContent =
    "قیمت عمده: " + money(product.wholesale) + " تومان · " + product.process + " · " + product.quality;

  var feat = document.getElementById("product-features");
  feat.innerHTML = product.features
    .map(function (line) {
      return "<li>" + line + "</li>";
    })
    .join("");

  if (product.deal && product.oldRetail) {
    var priceEl = document.getElementById("product-price");
    priceEl.innerHTML =
      "<s style='opacity:.55;font-size:.55em;margin-left:10px'>" +
      money(product.oldRetail) +
      "</s>" +
      money(product.retail) +
      " تومان";
  }

  var qty = 1;
  var qtyEl = document.getElementById("qty-value");
  document.getElementById("qty-minus").addEventListener("click", function () {
    if (qty > 1) {
      qty -= 1;
      qtyEl.textContent = qty.toLocaleString("fa-IR");
    }
  });
  document.getElementById("qty-plus").addEventListener("click", function () {
    if (qty < 99) {
      qty += 1;
      qtyEl.textContent = qty.toLocaleString("fa-IR");
    }
  });

  document.querySelectorAll(".pd-chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      var row = chip.parentElement;
      row.querySelectorAll(".pd-chip").forEach(function (c) {
        c.classList.remove("is-on");
      });
      chip.classList.add("is-on");
    });
  });

  var pack = document.getElementById("product-package");
  document.getElementById("thumbs").addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-thumb]");
    if (!btn) return;
    document.querySelectorAll("#thumbs button").forEach(function (b) {
      b.classList.toggle("is-on", b === btn);
    });
    pack.classList.toggle("is-alt", btn.getAttribute("data-thumb") !== "0");
  });

  var toast = document.getElementById("toast");
  var toastTimer;
  document.getElementById("add-cart").addEventListener("click", function () {
    toast.hidden = false;
    toast.textContent = qty.toLocaleString("fa-IR") + " عدد «" + product.name + "» به سبد اضافه شد";
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toast.hidden = true;
    }, 2200);
  });

  var detailsName = document.getElementById("details-pack-name");
  var detailsIntro = document.getElementById("details-intro");
  var detailsBullets = document.getElementById("details-bullets");
  if (detailsName) detailsName.textContent = product.name;
  if (detailsIntro) detailsIntro.textContent = product.desc;
  if (detailsBullets) {
    detailsBullets.innerHTML = product.features
      .slice(0, 4)
      .map(function (line) {
        return "<li>" + line + "</li>";
      })
      .join("");
  }

  var tabs = document.querySelectorAll(".pd-tab");
  var panels = document.querySelectorAll(".pd-tab-panel");
  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      var id = tab.getAttribute("data-tab");
      tabs.forEach(function (t) {
        var on = t === tab;
        t.classList.toggle("is-on", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
      });
      panels.forEach(function (panel) {
        var show = panel.getAttribute("data-panel") === id;
        panel.classList.toggle("is-on", show);
        panel.hidden = !show;
      });
    });
  });

  function starGlyphs(n, filled) {
    var s = "";
    for (var i = 1; i <= 5; i++) s += i <= n ? filled : "☆";
    return s;
  }

  function scoreText(stars) {
    return (3.8 + stars * 0.24).toFixed(1).replace(".", "٫");
  }

  function reviewCount(stars) {
    return 12 + stars * 7;
  }

  var sampleReviews = [
    {
      name: "سوزان م.",
      verified: true,
      date: "۱۴۰۴/۰۶/۰۲",
      stars: 5,
      title: "عطر فوق‌العاده",
      body: "برای مهمانی پختیم؛ دانه‌ها بلند و عطر دم‌سیاه عالی بود. قطعاً دوباره می‌خرم.",
      reply: null
    },
    {
      name: "کاربر مهمان",
      verified: false,
      date: "۱۴۰۴/۰۵/۲۰",
      stars: 3,
      title: "قیمت کمی بالا",
      body: "کیفیت خوب است ولی نسبت به بسته مشابه، قیمت را کمی بالاتر دیدم. طعم قابل قبول بود.",
      reply: null
    },
    {
      name: "مهدی ر.",
      verified: true,
      date: "۱۴۰۴/۰۵/۱۰",
      stars: 4,
      title: "پخت یکدست",
      body: "با دستور پخت صفحه، برنج نرم و دانه‌دانه شد. فقط دوست داشتم راهنمای شستشو واضح‌تر باشد.",
      reply: {
        name: "برنج‌کِر",
        date: "۱۴۰۴/۰۵/۱۱",
        body: "متشکریم از نظرتان. برای این محصول یک‌بار آبکشی ملایم کافی است؛ اگر سوالی داشتید به پشتیبانی پیام دهید."
      }
    },
    {
      name: "نرگس ک.",
      verified: true,
      date: "۱۴۰۴/۰۴/۲۸",
      stars: 5,
      title: "بسته‌بندی تمیز",
      body: "بسته سالم رسید و برنج تازه بود. برای مصرف خانواده عالی است.",
      reply: null
    }
  ];

  var reviewsScore = document.getElementById("reviews-score");
  var reviewsStars = document.getElementById("reviews-stars");
  var reviewsBased = document.getElementById("reviews-based");
  var reviewsList = document.getElementById("reviews-list");
  var count = reviewCount(product.stars);

  if (reviewsScore) reviewsScore.textContent = scoreText(product.stars);
  if (reviewsStars) reviewsStars.textContent = starGlyphs(product.stars, "★");
  if (reviewsBased) reviewsBased.textContent = "بر اساس " + count.toLocaleString("fa-IR") + " نظر";

  function renderReviews(list) {
    if (!reviewsList) return;
    reviewsList.innerHTML = list
      .map(function (r) {
        var replyHtml = "";
        if (r.reply) {
          replyHtml =
            '<aside class="pd-review-reply">' +
            '<div class="pd-review-reply-head"><strong>' +
            r.reply.name +
            '</strong><span class="pd-review-date">' +
            r.reply.date +
            "</span></div><p>" +
            r.reply.body +
            "</p></aside>";
        }
        return (
          '<article class="pd-review">' +
          '<div class="pd-review-meta"><div class="pd-review-who"><strong>' +
          r.name +
          "</strong>" +
          (r.verified ? '<span class="pd-review-verified">خریدار تأییدشده</span>' : "") +
          '</div><span class="pd-review-date">' +
          r.date +
          "</span></div>" +
          '<div class="pd-review-title-row"><span class="pd-review-stars" aria-hidden="true">' +
          starGlyphs(r.stars, "★") +
          '</span><span class="pd-review-title">' +
          r.title +
          "</span></div>" +
          '<p class="pd-review-body">' +
          r.body +
          "</p>" +
          '<p class="pd-review-product">' +
          product.name +
          " — " +
          product.quality +
          "</p>" +
          replyHtml +
          "</article>"
        );
      })
      .join("");
  }

  renderReviews(sampleReviews);

  var form = document.getElementById("review-form");
  var writeBtn = document.getElementById("write-review");
  var cancelBtn = document.getElementById("review-cancel");
  if (writeBtn && form) {
    writeBtn.addEventListener("click", function () {
      form.hidden = false;
      form.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  }
  if (cancelBtn && form) {
    cancelBtn.addEventListener("click", function () {
      form.hidden = true;
      form.reset();
    });
  }
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var title = document.getElementById("review-title").value.trim();
      var body = document.getElementById("review-body").value.trim();
      if (!title || !body) return;
      sampleReviews.unshift({
        name: "شما",
        verified: true,
        date: "امروز",
        stars: product.stars,
        title: title,
        body: body,
        reply: null
      });
      renderReviews(sampleReviews);
      form.hidden = true;
      form.reset();
      if (reviewsBased) {
        reviewsBased.textContent =
          "بر اساس " + (count + 1).toLocaleString("fa-IR") + " نظر";
      }
    });
  }
})();
