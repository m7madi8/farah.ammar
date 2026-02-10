/**
 * ProductDetailPage — single product view with hero image, details, and Add to cart / Pay buttons.
 * Data from API by slug (route param). Deep link: /product/:slug.
 */

import { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { NO_DETAIL_PAGE_SLUGS } from '../constants/products';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { CartPanel } from '../components/CartPanel';
import { CartToast } from '../components/CartToast';
import { useLanguage } from '../context/LanguageContext';
import { useCart } from '../context/CartContext';
import { fetchProductBySlug } from '../services/api';

export function ProductDetailPage({ cartOpen, onCartOpen, setCartOpen }) {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { t, lang } = useLanguage();
  const { addItem } = useCart();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toastShow, setToastShow] = useState(false);

  // Products with no detail page: redirect to home
  useEffect(() => {
    if (slug && NO_DETAIL_PAGE_SLUGS.includes(slug)) {
      navigate('/', { replace: true });
      return;
    }
  }, [slug, navigate]);

  useEffect(() => {
    let cancelled = false;
    fetchProductBySlug(slug).then((p) => {
      if (!cancelled) {
        setProduct(p);
        setLoading(false);
      }
    }).catch(() => {
      if (!cancelled) setLoading(false);
    });
    return () => { cancelled = true; };
  }, [slug]);

  if (loading || !product) {
    return (
      <>
        <Navbar backToShop alwaysShowBackground onCartClick={onCartOpen ? () => onCartOpen(true) : undefined} />
        <main className="product-main" style={{ padding: '4rem 1rem', textAlign: 'center' }}>
          {loading ? <p>{lang === 'ar' ? 'جاري التحميل...' : 'Loading...'}</p> : (
            <>
              <p>{lang === 'ar' ? 'المنتج غير موجود' : 'Product not found'}</p>
              <Link to="/">{(lang === 'ar' ? 'الرئيسية' : 'Home')}</Link>
            </>
          )}
        </main>
      </>
    );
  }

  const name = lang === 'ar' && product.nameAr ? product.nameAr : product.name;
  const desc = lang === 'ar' && product.descriptionAr ? product.descriptionAr : product.description;

  const handleAddToCart = () => {
    addItem(product);
    setToastShow(true);
  };

  return (
    <>
      <Navbar backToShop={false} alwaysShowBackground onCartClick={onCartOpen ? () => onCartOpen(true) : undefined} />
      <CartPanel isOpen={cartOpen} onClose={() => setCartOpen?.(false)} />
      <CartToast show={toastShow} onHide={() => setToastShow(false)} />
      <main className="product-main">
        <div className="product-hero">
          <div className="product-hero-image product-hero-anim">
            <picture>
              <img
                src={product.heroImage || product.imageUrl}
                alt={name}
                width="1200"
                height="750"
                decoding="async"
              />
            </picture>
          </div>
          <div className="product-hero-overlay product-hero-anim" />
        </div>
        <div className="product-content product-content-anim">
          <div className="product-content-inner product-content-anim">
            <button
              type="button"
              className="product-back"
              onClick={() => {
                navigate('/');
                setTimeout(() => {
                  const el = document.getElementById('product');
                  if (el) el.scrollIntoView({ behavior: 'smooth' });
                }, 80);
              }}
            >
              <i className="bi bi-arrow-left" aria-hidden="true" />
              <span>{t('product.backHome')}</span>
            </button>
            <header className="product-header">
              <h1 className="product-name">{name}</h1>
              <div className="product-preview-price-wrap">
                <span className="product-preview-price">{product.price}</span>
                <span className="product-preview-currency">₪</span>
              </div>
              <p className="product-lead">{desc}</p>
            </header>
            {product.details && product.details.length > 0 && (
              <section className="product-details">
                <h2 className="product-details-title">{t('product.inside')}</h2>
                <ul className="product-details-list">
                  {product.details.map((key) => (
                    <li key={key}>{t(`product.${key}`)}</li>
                  ))}
                </ul>
              </section>
            )}
            <section className="product-buy" id="buy">
              <h2 className="product-buy-title">{t('product.buyTitle')}</h2>
              <p className="product-buy-desc">{t('product.buyDesc')}</p>
              <div className="product-buy-btns">
                <button
                  type="button"
                  className="product-btn product-btn-cart"
                  onClick={handleAddToCart}
                >
                  <i className="bi bi-bag-plus" aria-hidden="true" />
                  <span>{t('product.addToCart')}</span>
                </button>
                <a
                  href={`https://wa.me/972501234567?text=${encodeURIComponent(
                    `Hi, I want to order ${name} (${product.price}₪) - Pay by Visa/Mastercard`
                  )}`}
                  className="product-btn product-btn-pay"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <i className="bi bi-credit-card-2-front" aria-hidden="true" />
                  <span>{t('product.btnPay')}</span>
                </a>
                <a
                  href={`https://wa.me/972501234567?text=${encodeURIComponent(
                    `Hi, I want to order ${name} (${product.price}₪) - Cash on delivery`
                  )}`}
                  className="product-btn product-btn-cod"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <i className="bi bi-cash-stack" aria-hidden="true" />
                  <span>{t('product.btnCod')}</span>
                </a>
              </div>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
