/**
 * API service for Chef Farah Ammar store.
 * All product, cart, and order data should come from REST endpoints.
 * Set VITE_API_BASE in .env (e.g. https://api.example.com) or leave empty for mock.
 */

const BASE = import.meta.env.VITE_API_BASE || '';

/**
 * Fallback product list when API is not configured (for development / static deploy).
 * Backend should expose GET /products returning array of { id, slug, name, nameAr, description, descriptionAr, price, category, imageUrl, order, details[] }.
 */
const MOCK_PRODUCTS = [
  { id: '1', slug: 'dumplings-chicken', name: 'Dumplings – Chicken', nameAr: 'دامبلنغ – دجاج', description: 'Handcrafted chicken dumplings with rich flavors. Created by Chef Farah.', descriptionAr: 'دامبلنغ دجاج مصنوع يدوياً بنكهات غنية. من إبداع الشيف فرح.', price: 25, category: 'boxes', imageUrl: '/img/1.png', heroImage: '/img/2.png', order: 1, badge: 'Signature', details: ['detail1', 'detail2', 'detail3', 'detail4', 'detail5', 'detailTeriyaki', 'detailSweetChili', 'detail6'] },
  { id: '2', slug: 'dumplings-meat', name: 'Dumplings – Meat', nameAr: 'دامبلنغ – لحم', description: 'Handcrafted meat dumplings with rich flavors. Created by Chef Farah.', descriptionAr: 'دامبلنغ لحم مصنوع يدوياً بنكهات غنية. من إبداع الشيف فرح.', price: 27, category: 'boxes', imageUrl: '/img/1.png', heroImage: '/img/2.png', order: 2, badge: 'Signature', details: ['detail1', 'detail2Meat', 'detail3', 'detail4', 'detail5', 'detailTeriyaki', 'detailSweetChili', 'detail6'] },
  { id: '3', slug: 'teriyaki-sauce', name: 'Teriyaki sauce', nameAr: 'صلصة ترياكي', description: 'Rich teriyaki glaze, perfect for dumplings and stir-fry.', descriptionAr: 'صلصة ترياكي غنية، مثالية للدامبلنغ والقلي السريع.', price: 2, category: 'sauces', imageUrl: '/img/teriyaki.jpeg', heroImage: '/img/teriyaki.jpeg', order: 3, badge: 'Sauce', details: [] },
  { id: '4', slug: 'soya-sauce', name: 'Soya sauce', nameAr: 'صلصة صويا', description: 'Classic soy sauce for dipping and cooking.', descriptionAr: 'صلصة صويا كلاسيكية للغمس والطبخ.', price: 2, category: 'sauces', imageUrl: '/img/soya.jpeg', heroImage: '/img/soya.jpeg', order: 4, badge: 'Sauce', details: [] },
  { id: '5', slug: 'buffalo-sauce', name: 'Buffalo sauce', nameAr: 'صلصة بافلو', description: 'Spicy buffalo sauce for a bold kick.', descriptionAr: 'صلصة بافلو حارة لمذاق قوي.', price: 2, category: 'sauces', imageUrl: '/img/buffalo.jpeg', heroImage: '/img/buffalo.jpeg', order: 5, badge: 'Sauce', details: [] },
  { id: '6', slug: 'sweet-chili-sauce', name: 'Sweet chili sauce', nameAr: 'صلصة الفلفل الحلو', description: 'Sweet and tangy chili sauce for dipping.', descriptionAr: 'صلصة فلفل حلوة وحامضة للغمس.', price: 2, category: 'sauces', imageUrl: '/img/sweet-chili.jpeg', heroImage: '/img/sweet-chili.jpeg', order: 6, badge: 'Sauce', details: [] },
  { id: '7', slug: 'chop-sticks', name: 'Chop sticks', nameAr: 'عيدان الطعام', description: '1 ₪ per stick (not per pack).', descriptionAr: '1 ₪ للعود الواحد (وليس للمجموعة).', price: 1, category: 'chopsticks', imageUrl: '/img/chop-sticks.jpeg', heroImage: '/img/chop-sticks.jpeg', order: 7, badge: 'Accessory', details: [] },
];

async function request(path, options = {}) {
  const url = BASE ? `${BASE.replace(/\/$/, '')}${path}` : null;
  if (!url) return null;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

function toFilterCategory(value) {
  if (value == null || value === '') return '';
  const s = String(value).trim().toLowerCase();
  if (s === 'boxes' || s === 'dumplings' || s === 'box') return 'boxes';
  if (s === 'sauces' || s === 'sauce') return 'sauces';
  if (s === 'chopsticks' || s === 'chop-sticks' || s === 'chop_sticks') return 'chopsticks';
  return '';
}

function inferCategoryFromProduct(p) {
  const raw = p.category ?? p.categories?.[0]?.category?.slug ?? p.categories?.[0]?.slug ?? (typeof p.categories?.[0]?.category === 'string' ? p.categories[0].category : '');
  const fromSlug = toFilterCategory(typeof raw === 'string' ? raw : (raw?.slug != null ? String(raw.slug) : ''));
  if (fromSlug) return fromSlug;
  const slug = (p.slug || '').toLowerCase();
  const badge = (p.badge || '').toLowerCase();
  if (slug.includes('sauce') || badge.includes('sauce')) return 'sauces';
  if (slug.includes('chop') || slug.includes('stick')) return 'chopsticks';
  return 'boxes';
}

function normalizeProduct(p) {
  const category = inferCategoryFromProduct(p);
  const heroImg = p.hero_image ?? p.images?.find((i) => i.is_hero) ?? p.images?.[0];
  const imageUrl = typeof heroImg === 'string' ? heroImg : (heroImg?.url ?? p.imageUrl);
  return {
    ...p,
    name: p.name ?? p.name_en,
    nameAr: p.nameAr ?? p.name_ar,
    description: p.description ?? p.description_en,
    descriptionAr: p.descriptionAr ?? p.description_ar,
    imageUrl: imageUrl ?? p.imageUrl,
    order: p.order ?? p.sort_order ?? 0,
    category,
  };
}

/**
 * Fetch all products. Uses mock when VITE_API_BASE not set, or when API fails/returns empty.
 * Each product gets .category = 'boxes' | 'sauces' | 'chopsticks' for filtering.
 */
export async function fetchProducts() {
  if (!BASE) return MOCK_PRODUCTS.map(normalizeProduct);
  try {
    const data = await request('/products');
    const raw = Array.isArray(data) ? data : (data?.results ?? data?.products ?? []);
    const list = Array.isArray(raw) ? raw : [];
    if (list.length > 0) return list.map(normalizeProduct);
  } catch (_) { /* API failed: fall back to mock */ }
  return MOCK_PRODUCTS.map(normalizeProduct);
}

/**
 * Fetch single product by slug. Used for product detail page.
 */
export async function fetchProductBySlug(slug) {
  const products = await fetchProducts();
  return products.find((p) => p.slug === slug) || null;
}

/**
 * Submit order to backend. POST /orders with body { name, phone, address, notes, items: [{ productId, quantity, price, name }], total }.
 * When API is not set, returns a local success object so checkout still works (e.g. for demo).
 */
export async function submitOrder(orderPayload) {
  if (!BASE) {
    return { ok: true, orderId: `ord-${Date.now()}` };
  }
  return request('/orders', {
    method: 'POST',
    body: JSON.stringify(orderPayload),
  });
}
