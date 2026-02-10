/**
 * Category filter example — products from a FIXED source, filter by category.
 * Why products don't disappear: we keep one products array in state and only
 * compute a filtered list for display. The source (products) never changes when
 * you click a category; only the selected category and thus the displayed list change.
 */
import { useState, useMemo } from 'react';

const CATEGORIES = [
  { key: 'all', label: 'All' },
  { key: 'sauces', label: 'Sauces' },
  { key: 'chopsticks', label: 'Chop sticks' },
  { key: 'boxes', label: 'Dumplings' },
];

// Fixed source — never replaced, only read from
const SAMPLE_PRODUCTS = [
  { id: 1, name: 'Teriyaki sauce', category: 'sauces', price: 2 },
  { id: 2, name: 'Soya sauce', category: 'sauces', price: 2 },
  { id: 3, name: 'Chop sticks', category: 'chopsticks', price: 1 },
  { id: 4, name: 'Dumplings – Chicken', category: 'boxes', price: 25 },
  { id: 5, name: 'Sweet chili sauce', category: 'sauces', price: 2 },
  { id: 6, name: 'Dumplings – Meat', category: 'boxes', price: 27 },
];

export function CategoryFilterExample() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [products] = useState(SAMPLE_PRODUCTS);

  const filteredProducts = useMemo(() => {
    if (selectedCategory === 'all') return products;
    return products.filter((p) => p.category === selectedCategory);
  }, [products, selectedCategory]);

  return (
    <div style={{ padding: '1.5rem', maxWidth: 600, margin: '0 auto' }}>
      <h2>Shop</h2>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            type="button"
            onClick={() => setSelectedCategory(cat.key)}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: 999,
              border: selectedCategory === cat.key ? '2px solid #5a2d82' : '1px solid #ccc',
              background: selectedCategory === cat.key ? '#5a2d82' : '#fff',
              color: selectedCategory === cat.key ? '#fff' : '#333',
              cursor: 'pointer',
            }}
          >
            {cat.label}
          </button>
        ))}
      </div>

      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {filteredProducts.map((product) => (
          <li
            key={product.id}
            style={{
              padding: '0.75rem',
              marginBottom: '0.5rem',
              background: '#f8f9fa',
              borderRadius: 8,
              border: '1px solid #eee',
            }}
          >
            <strong>{product.name}</strong> — {product.category} — {product.price} ₪
          </li>
        ))}
      </ul>

      {filteredProducts.length === 0 && (
        <p style={{ color: '#666' }}>No products in this category.</p>
      )}
    </div>
  );
}

/**
 * How it works:
 *
 * 1. Fixed source: `products` is set once from SAMPLE_PRODUCTS and never replaced.
 *    We don't refetch or overwrite it when the user clicks a category.
 *
 * 2. Selected category: `selectedCategory` is the only thing that changes on click.
 *    "All" → 'all', "Sauces" → 'sauces', etc.
 *
 * 3. Display list: `filteredProducts` is derived from `products` + `selectedCategory`:
 *    - selectedCategory === 'all' → show all products
 *    - otherwise → show products where product.category === selectedCategory
 *
 * 4. So when you switch categories, we're just filtering the same fixed array.
 *    No new network request, no replacing state — so nothing disappears.
 */
