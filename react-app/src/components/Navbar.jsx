/**
 * Navbar — fixed top navigation with brand, language toggle, and cart button.
 * Presentational; receives cart count and handlers from parent/context.
 */

import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { useCart } from '../context/CartContext';

export function Navbar({ onCartClick, showCart = true, backToShop = false, alwaysShowBackground = false }) {
  const { t, lang, toggleLang } = useLanguage();
  const { itemCount } = useCart();
  const navRef = useRef(null);

  // Show header background when scrolled (nav-scrolled class), or always on checkout/product pages.
  // Throttled with requestAnimationFrame to avoid scroll lag on mobile.
  useEffect(() => {
    const nav = navRef.current;
    if (!nav) return;
    let ticking = false;
    const update = () => {
      const show = alwaysShowBackground || window.scrollY > 60;
      nav.classList.toggle('nav-scrolled', show);
      ticking = false;
    };
    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(update);
      }
    };
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [alwaysShowBackground]);

  return (
    <nav ref={navRef} className="nav-minimal fixed-top anim-fade-down" id="nav">
      <div className="container-fluid px-4">
        <Link className="nav-brand" to="/">
          {t('nav.brand')}
        </Link>
        <div className="nav-right">
          <button
            type="button"
            className="nav-lang-toggle"
            onClick={toggleLang}
            aria-label={lang === 'ar' ? 'Switch to English' : 'Switch to Arabic'}
            title={lang === 'ar' ? 'English' : 'العربية'}
          >
            <i className="bi bi-translate" aria-hidden="true" />
          </button>
          {backToShop ? (
            <Link className="nav-order" to="/#product">
              {t('checkout.backToShop')}
            </Link>
          ) : (
            <>
              {showCart && (
                <button
                  type="button"
                  className="nav-cart"
                  onClick={() => onCartClick?.()}
                  aria-label="Cart"
                  aria-expanded="false"
                  aria-haspopup="true"
                >
                  <i className="bi bi-cart3" aria-hidden="true" />
                  <span
                    className="nav-cart-badge"
                    aria-hidden={itemCount === 0}
                  >
                    {itemCount}
                  </span>
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
