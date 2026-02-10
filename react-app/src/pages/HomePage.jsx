/**
 * HomePage — container for Hero, Shop (filters, sort, product grid), Order block, and Footer.
 * Fetches products from API and manages filter/sort state.
 */

import { useState, useEffect, useMemo } from 'react';
import { Hero } from '../components/Hero';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { ProductCard } from '../components/ProductCard';
import { CartPanel } from '../components/CartPanel';
import { CartToast } from '../components/CartToast';
import { CookieConsent } from '../components/CookieConsent';
import { useLanguage } from '../context/LanguageContext';
import { fetchProducts } from '../services/api';

const FILTERS = [
  { key: 'all', label: 'filter.all', labelAr: 'الكل' },
  { key: 'boxes', label: 'filter.boxes', labelAr: 'دامبلنغ' },
  { key: 'sauces', label: 'filter.sauces', labelAr: 'الصوص' },
  { key: 'chopsticks', label: 'filter.chopsticks', labelAr: 'عيدان الطعام' },
];

export function HomePage({ onCartOpen, cartOpen, setCartOpen }) {
  const { t, lang } = useLanguage();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('newest');
  const [toastShow, setToastShow] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchProducts().then((data) => {
      if (!cancelled) {
        setProducts(Array.isArray(data) ? data : []);
        setLoading(false);
      }
    }).catch(() => {
      if (!cancelled) setLoading(false);
    });
    return () => { cancelled = true; };
  }, []);

  // Reveal elements with .anim-on-scroll when they enter the viewport (like original site)
  useEffect(() => {
    const els = document.querySelectorAll('.anim-on-scroll');
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -30px 0px' }
    );
    els.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [products]);

  const filtered = useMemo(() => {
    let list = filter === 'all' ? products : products.filter((p) => p.category === filter);
    list = [...list].sort((a, b) => {
      if (sort === 'newest') return (a.order || 0) - (b.order || 0);
      if (sort === 'price-asc') return (a.price || 0) - (b.price || 0);
      if (sort === 'price-desc') return (b.price || 0) - (a.price || 0);
      return 0;
    });
    return list;
  }, [products, filter, sort]);

  const emptyLabel = useMemo(() => {
    const f = FILTERS.find((x) => x.key === filter);
    const prefix = t('empty.inCategory');
    const label = f ? (lang === 'ar' ? f.labelAr : (t(f.label) || f.label)) : '';
    return `${prefix}${label}`;
  }, [filter, lang, t]);

  return (
    <>
      <PageLoader visible={loading && !products.length} />
      <Navbar onCartClick={onCartOpen} />
      <CartPanel isOpen={cartOpen} onClose={() => setCartOpen?.(false)} />
      <CartToast show={toastShow} onHide={() => setToastShow(false)} />

      <main>
        <Hero />
        <section className="block-product" id="product">
          <div className="shop-wrap">
            <header className="shop-header anim-on-scroll">
              <h2 className="shop-title">{t('shop.title')}</h2>
              <p className="shop-sub">{t('shop.sub')}</p>
            </header>
            <div className="shop-toolbar anim-on-scroll">
              <div className="shop-filters">
                {FILTERS.map((f) => (
                  <button
                    key={f.key}
                    type="button"
                    className={`shop-filter-btn ${filter === f.key ? 'active' : ''}`}
                    onClick={() => setFilter(f.key)}
                    aria-pressed={filter === f.key}
                    data-filter={f.key}
                  >
                    {t(f.label)}
                  </button>
                ))}
              </div>
              <div className="shop-sort">
                <label htmlFor="shopSort" className="shop-sort-label">{t('sort.label')}</label>
                <select
                  id="shopSort"
                  className="shop-sort-select"
                  aria-label="Sort products"
                  value={sort}
                  onChange={(e) => setSort(e.target.value)}
                >
                  <option value="newest">{t('sort.newest')}</option>
                  <option value="price-asc">{t('sort.priceAsc')}</option>
                  <option value="price-desc">{t('sort.priceDesc')}</option>
                </select>
              </div>
            </div>
            <p className="shop-swipe-hint">{t('shop.swipeHint')}</p>
            <div className="shop-grid">
              {filtered.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onShowToast={() => setToastShow(true)}
                />
              ))}
            </div>
            {filtered.length === 0 && (
              <div className="shop-empty" aria-live="polite">
                <i className="bi bi-inbox" />
                <p className="shop-empty-title">{emptyLabel}</p>
                <p className="shop-empty-desc">{t('empty.desc')}</p>
                <button
                  type="button"
                  className="shop-empty-btn"
                  onClick={() => setFilter('all')}
                >
                  {t('empty.showAll')}
                </button>
              </div>
            )}
          </div>
        </section>
        <section className="block-order" id="order">
          <div className="order-inner">
            <h2 className="order-title anim-on-scroll">{t('order.title')}</h2>
            <p className="order-sub anim-on-scroll">{t('order.sub')}</p>
            <a
              href="https://wa.me/972501234567"
              className="btn-order btn-order-wa anim-on-scroll"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="bi bi-whatsapp" /> <span>{t('order.wa')}</span>
            </a>
          </div>
        </section>
        <Footer />
      </main>
      <CookieConsent />
    </>
  );
}

function PageLoader({ visible }) {
  const [show, setShow] = useState(visible);
  useEffect(() => {
    if (!visible && show) {
      const el = document.getElementById('pageLoader');
      if (el) {
        el.classList.add('loader-out');
        const tmr = setTimeout(() => setShow(false), 450);
        return () => clearTimeout(tmr);
      }
    }
    setShow(visible);
  }, [visible, show]);
  if (!show) return null;
  return (
    <div className="page-loader" id="pageLoader">
      <div className="loader-inner">
        <img src="/img/logo.png" alt="Chef Farah Ammar" className="loader-logo" width="220" height="110" decoding="async" />
        <div className="loader-bar"><span className="loader-bar-fill" /></div>
      </div>
    </div>
  );
}
