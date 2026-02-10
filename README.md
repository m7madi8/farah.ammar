# Chef Farah Ammar — مشروع الموقع

## هيكل المشروع (الفرونت اند)

```
فرح/
├── index.html              # الصفحة الرئيسية
├── css/                    # ملفات التنسيق
│   ├── style.css           # التنسيق الرئيسي + التحقق من الطلب
│   ├── product.css         # صفحات المنتجات
│   └── dashboard.css       # لوحة التحكم
├── js/                     # سكربتات الجافاسكربت
│   ├── i18n.js             # الترجمة (عربي / إنجليزي)
│   ├── cart.js             # السلة والدفع
│   └── dashboard.js        # لوحة التحكم والطلبات
├── img/                    # الصور
│   ├── logo.png, logo1.png, 1.png, 2.png
│   ├── teriyaki.jpeg, soya.jpeg, buffalo.jpeg
│   ├── sweet-chili.jpeg, chop-sticks.jpeg
│   └── (أضف logo2.png للمعاينة عند المشاركة إن رغبت)
├── pages/                  # الصفحات الداخلية
│   ├── checkout.html       # تأكيد الطلب (دفع عند الاستلام)
│   ├── dashboard.html      # لوحة التحكم
│   ├── product.html
│   ├── product-dumplings-chicken.html
│   └── product-dumplings-meat.html
├── logo.psd, logo1.ai      # مصادر التصميم (اختياري)
├── BRAND-STRATEGY.md
└── README.md
```

## التشغيل

- افتح `index.html` في المتصفح أو استضف المجلد على GitHub Pages / أي خادم ثابت.
- الصفحة الرئيسية تستخدم `css/` و `js/` و `pages/` تلقائياً.

## ملاحظات

- الطلبات (دفع عند الاستلام) تُحفظ في `localStorage` وتظهر في لوحة التحكم.
- لوحة التحكم: افتح `pages/dashboard.html` لعرض الطلبات وطباعة الفواتير.
