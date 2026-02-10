# Nana's Bites — React App

React conversion of the Chef Farah Ammar store. Ready to connect to a backend API.

## Structure

```
src/
├── components/     # Reusable UI (Navbar, Footer, ProductCard, OrderSummary, CartPanel, etc.)
├── pages/          # Container pages (HomePage, ProductDetailPage, CheckoutPage)
├── context/        # CartContext (cart state), LanguageContext (i18n)
├── services/       # api.js — fetch products, submit order (REST)
├── data/           # translations.js (en / ar)
├── styles/         # style.css, product.css (existing design)
├── App.jsx
└── index.jsx
```

## Scripts

- `npm run dev` — start dev server (port 3000)
- `npm run build` — production build
- `npm run preview` — preview production build

## Backend API

Set `VITE_API_BASE` in `.env` to your API root (e.g. `https://api.example.com`).

- **GET** `/products` — list products (id, slug, name, nameAr, description, descriptionAr, price, category, imageUrl, heroImage, order, badge, details[])
- **GET** `/products/:slug` — optional; app resolves by slug from list
- **POST** `/orders` — body: `{ name, phone, address, notes, items: [{ productId, name, price, quantity }], total }`

If `VITE_API_BASE` is not set, the app uses mock product data and accepts orders locally (success response, cart cleared).

## Routing

- `/` — Home (hero, shop grid, filters, sort)
- `/product/:slug` — Product detail (e.g. `/product/dumplings-chicken`)
- `/checkout` — Checkout form (name, phone, address, notes); client-side validation

## Features

- **Cart:** Context API; product ID, quantity, price, total; persists in `localStorage`
- **i18n:** English / Arabic; `LanguageContext` + `translations.js`
- **Design:** Existing CSS kept; responsive layout preserved
- **Forms:** Checkout validated (required name, phone, address); errors shown
