/* Farah Ammar — i18n: English / العربية */
(function () {
  var STORAGE_KEY = 'farah-lang';

  var translations = {
    en: {
      'nav.brand': 'Farah Ammar',
      'nav.order': 'Order',
      'nav.back': 'Back',
      'hero.byline': 'Gourmet Bites & Sweets',
      'hero.title': "Nana's Bites by Chef Farah Ammar",
      'hero.tagline': 'Tasting the world, One bite at a time.',
      'hero.subtext': 'Small-batch desserts and gourmet treats. Thoughtful, elegant, unforgettable.',
      'hero.cta': 'Explore the Collection',
      'hero.scroll': 'Scroll',
      'shop.title': 'Shop',
      'shop.sub': 'Artisan sweets & gifts, crafted by Chef Farah',
      'filter.all': 'All',
      'filter.boxes': 'Dessert Boxes',
      'filter.gifts': 'Gifts',
      'sort.label': 'Sort by',
      'sort.aria': 'Sort products',
      'sort.newest': 'Newest',
      'sort.priceAsc': 'Price: low to high',
      'sort.priceDesc': 'Price: high to low',
      'product.badge': 'Signature',
      'product.cardTitle': "Nana's Bites – Signature Dumplings",
      'product.cardDesc': 'Handcrafted dumplings with rich flavors, wrapped to perfection. Created by Chef Farah Ammar for moments worth savoring.',
      'product.viewProduct': 'View product',
      'empty.title': 'No products in this category',
      'empty.inCategory': 'No products in ',
      'empty.desc': "We don't have any items here yet. Try another filter or check back soon.",
      'empty.showAll': 'Show all',
      'order.title': 'Other inquiries',
      'order.sub': "Questions? Special requests? We're here for you.",
      'order.wa': 'Contact us via WhatsApp',
      'footer.tagline': 'by Chef Farah Ammar · Crafted with love',
      'footer.connect': 'Connect',
      'footer.payment': 'Payment',
      'footer.cod': 'Cash on delivery',
      'footer.copy': "Nana's Bites by Chef Farah Ammar. All rights reserved.",
      'product.backHome': 'Back to home',
      'product.inside': "What's inside",
      'product.lead': 'Handcrafted dumplings made with care and tradition, filled with rich flavors and wrapped to perfection. Created by Chef Farah Ammar for moments worth savoring.',
      'product.detail1': 'Hand-rolled wheat dough, delicately prepared',
      'product.detail2': 'Fresh chicken filling',
      'product.detail3': 'Cabbage and green onions',
      'product.detail4': 'Garlic and ginger for warm depth',
      'product.detail5': 'Soy sauce and sesame oil',
      'product.detail6': 'Carefully selected spices',
      'product.buyTitle': 'Order now',
      'product.buyDesc': "Choose your payment method and we'll confirm via WhatsApp.",
      'product.btnPay': 'Pay by Visa / Mastercard',
      'product.btnCod': 'Cash on delivery',
      'product.footerTagline': 'Dessert box · Crafted with love',
      'cookie.msg': 'We use cookies to improve your experience and remember your preferences on this site.',
      'cookie.accept': 'Accept',
      'cookie.ignore': 'Ignore'
    },
    ar: {
      'nav.brand': 'فرح عمار',
      'nav.order': 'طلب',
      'nav.back': 'رجوع',
      'hero.byline': 'لقمات وحلويات فاخرة',
      'hero.title': 'نانا بايتس من الشيف فرح عمار',
      'hero.tagline': 'تذوق العالم، قضمةً قضمةً.',
      'hero.subtext': 'حلويات وقطع فاخرة بكميات محدودة. مدروسة، أنيقة، لا تُنسى.',
      'hero.cta': 'استكشف المجموعة',
      'hero.scroll': 'تمرير',
      'shop.title': 'المتجر',
      'shop.sub': 'حلويات وهدايا حرفية من الشيف فرح',
      'filter.all': 'الكل',
      'filter.boxes': 'صناديق الحلويات',
      'filter.gifts': 'الهدايا',
      'sort.label': 'ترتيب حسب',
      'sort.aria': 'ترتيب المنتجات',
      'sort.newest': 'الأحدث',
      'sort.priceAsc': 'السعر: من الأقل للأعلى',
      'sort.priceDesc': 'السعر: من الأعلى للأقل',
      'product.badge': 'توقيع',
      'product.cardTitle': 'نانا بايتس – دامبلنغ التوقيع',
      'product.cardDesc': 'دامبلنغ مصنوع يدوياً بنكهات غنية ومُلفوف بإتقان. من إبداع الشيف فرح عمار لحظات تستحق التذوق.',
      'product.viewProduct': 'عرض المنتج',
      'empty.title': 'لا منتجات في هذا التصنيف',
      'empty.inCategory': 'لا منتجات في ',
      'empty.desc': 'لا توجد منتجات هنا حالياً. جرّب تصفية أخرى أو عد قريباً.',
      'empty.showAll': 'عرض الكل',
      'order.title': 'استفسارات أخرى',
      'order.sub': 'أسئلة؟ طلبات خاصة؟ نحن هنا من أجلك.',
      'order.wa': 'تواصل معنا عبر واتساب',
      'footer.tagline': 'من الشيف فرح عمار · صنع بمحبة',
      'footer.connect': 'تواصل',
      'footer.payment': 'الدفع',
      'footer.cod': 'دفع عند الاستلام',
      'footer.copy': 'نانا بايتس من الشيف فرح عمار. جميع الحقوق محفوظة.',
      'product.backHome': 'العودة للرئيسية',
      'product.inside': 'ما بداخله',
      'product.lead': 'دامبلنغ مصنوع يدوياً بعناية وتقليد، مليء بالنكهات الغنية وملفوف بإتقان. من إبداع الشيف فرح عمار لحظات تستحق التذوق.',
      'product.detail1': 'عجينة قمح مُلفوفة يدوياً ومُعدّة بدقة',
      'product.detail2': 'حشوة دجاج طازجة',
      'product.detail3': 'ملفوف وبصل أخضر',
      'product.detail4': 'ثوم وزنجبيل لعمق دافئ',
      'product.detail5': 'صلصة الصويا وزيت السمسم',
      'product.detail6': 'بهارات مُختارة بعناية',
      'product.buyTitle': 'اطلب الآن',
      'product.buyDesc': 'اختر طريقة الدفع وسنؤكد عبر واتساب.',
      'product.btnPay': 'الدفع بفيزا / ماستركارد',
      'product.btnCod': 'دفع عند الاستلام',
      'product.footerTagline': 'صندوق الحلويات · صنع بمحبة',
      'cookie.msg': 'نستخدم ملفات تعريف الارتباط لتحسين تجربتك وتذكر تفضيلاتك على الموقع.',
      'cookie.accept': 'موافق',
      'cookie.ignore': 'تجاهل'
    }
  };

  function getStoredLang() {
    try {
      var s = localStorage.getItem(STORAGE_KEY);
      return s === 'ar' || s === 'en' ? s : 'en';
    } catch (e) { return 'en'; }
  }

  function setStoredLang(lang) {
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
  }

  function applyToPage(lang) {
    var t = translations[lang] || translations.en;
    var root = document.getElementById('htmlRoot') || document.documentElement;
    root.lang = lang;
    root.dir = lang === 'ar' ? 'rtl' : 'ltr';

    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      var val = t[key];
      if (val !== undefined) el.textContent = val;
    });

    document.querySelectorAll('[data-i18n-aria]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-aria');
      var val = t[key];
      if (val !== undefined) el.setAttribute('aria-label', val);
    });

    document.querySelectorAll('[data-i18n-title]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-title');
      var val = t[key];
      if (val !== undefined) el.setAttribute('title', val);
    });

    document.querySelectorAll('select[data-i18n-aria] option').forEach(function (opt) {
      var key = opt.getAttribute('data-i18n');
      if (key && t[key] !== undefined) opt.textContent = t[key];
    });

    var toggle = document.getElementById('navLangToggle');
    if (toggle) {
      toggle.setAttribute('title', lang === 'ar' ? 'English' : 'العربية');
      toggle.setAttribute('aria-label', lang === 'ar' ? 'Switch to English' : 'التبديل للعربية');
    }

    window.currentLang = lang;
    setStoredLang(lang);
    window.dispatchEvent(new CustomEvent('languageChange', { detail: { lang: lang } }));
  }

  function toggleLang() {
    var next = window.currentLang === 'ar' ? 'en' : 'ar';
    applyToPage(next);
  }

  window.currentLang = getStoredLang();
  window.applyLanguage = applyToPage;
  window.toggleLanguage = toggleLang;
  window.getTranslation = function (key) { return (translations[window.currentLang] || translations.en)[key]; };
  window.getEmptyInCategoryPrefix = function () { return window.getTranslation('empty.inCategory'); };

  document.addEventListener('DOMContentLoaded', function () {
    applyToPage(window.currentLang);
    var btn = document.getElementById('navLangToggle');
    if (btn) btn.addEventListener('click', toggleLang);
  });
})();
