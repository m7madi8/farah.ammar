/**
 * HomePage — Hero, Shop (product grid), Order block, Footer.
 * Shop: products loaded once, displayed by order (no filter/sort UI).
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

export function HomePage({ onCartOpen, cartOpen, setCartOpen }) {
  const { t } = useLanguage();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toastShow, setToastShow] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchProducts()
      .then((list) => {
        if (!cancelled && Array.isArray(list)) setProducts(list);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

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

  const shopList = useMemo(() => {
    const list = [...products];
    const aOrd = (a) => Number(a.order) || 0;
    list.sort((a, b) => aOrd(a) - aOrd(b));
    return list;
  }, [products]);

  const emptyLabel = t('empty.title');

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
            <p className="shop-swipe-hint">{t('shop.swipeHint')}</p>
            <div className="shop-grid">
              {shopList.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onShowToast={() => setToastShow(true)}
                />
              ))}
            </div>
            {shopList.length === 0 && (
              <div className="shop-empty" aria-live="polite">
                <i className="bi bi-inbox" />
                <p className="shop-empty-title">{emptyLabel}</p>
                <p className="shop-empty-desc">{t('empty.desc')}</p>
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
        <img src="/img/logo.webp" alt="Chef Farah Ammar" className="loader-logo" width="220" height="110" decoding="async" />
        <div className="loader-bar"><span className="loader-bar-fill" /></div>
      </div>
    </div>
  );
}
