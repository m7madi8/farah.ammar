# Nana's Bites React — Testing

## Run tests

```bash
npm install
npm run test
```

Watch mode: `npm run test:watch`

## Stack

- **Vitest** — test runner (Vite-native)
- **React Testing Library** — component tests
- **jsdom** — DOM environment

## What's tested

- **services/api.test.js:** `fetchProducts` (returns array/mock), `fetchProductBySlug`, `submitOrder` (local success, POST when API base set).
- **components/ProductCard.test.jsx:** Renders name and price, add to cart button, `onShowToast` on click, link to product page for slug with detail, no link for sauces/chopsticks.

## Writing tests

- Place test files next to source (`*.test.js`, `*.test.jsx`) or in `src/test/`.
- Use `render()` with providers (LanguageProvider, CartProvider, MemoryRouter) when testing components that use context or router.
