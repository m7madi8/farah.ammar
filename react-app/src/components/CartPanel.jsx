/**
 * CartPanel — slide-out cart drawer with item list, total, and checkout/Pay Visa buttons.
 * Opens when user clicks cart icon in Navbar.
 */

import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { useCart } from '../context/CartContext';

export function CartPanel({ isOpen, onClose }) {
  const { t } = useLanguage();
  const { items, total, removeItem } = useCart();
  const count = items.length;

  return (
    <div
      className={`cart-panel ${isOpen ? 'cart-panel-open' : ''}`}
      role="dialog"
      aria-label="Shopping cart"
      aria-hidden={!isOpen}
    >
      <div className="cart-panel-inner">
        <div className="cart-panel-header">
          <h3 className="cart-panel-title">{t('cart.title')}</h3>
          <button
            type="button"
            className="cart-panel-close"
            onClick={onClose}
            aria-label="Close cart"
          >
            <i className="bi bi-x-lg" />
          </button>
        </div>
        <div className="cart-panel-list">
          {items.map((item, i) => (
            <div key={`${item.productId}-${i}`} className="cart-item" data-index={i}>
              <span className="cart-item-name">{item.name}</span>
              <span className="cart-item-price">
                {(item.price * (item.quantity || 1))} ₪
              </span>
              <button
                type="button"
                className="cart-item-remove"
                aria-label={t('cart.remove')}
                onClick={() => removeItem(i)}
              >
                {t('cart.remove')}
              </button>
            </div>
          ))}
        </div>
        {count === 0 && (
          <div className="cart-panel-empty">
            <i className="bi bi-cart-x" />
            <p>{t('cart.empty')}</p>
          </div>
        )}
        {count > 0 && (
          <div className="cart-panel-footer">
            <div className="cart-panel-total">
              <span>{t('cart.total')}</span>
              <span>{total} ₪</span>
            </div>
            <Link
              to="/checkout"
              className="cart-panel-order"
              onClick={onClose}
            >
              <span>{t('cart.orderViaWa')}</span>
            </Link>
            <a
              href={`https://wa.me/972501234567?text=${encodeURIComponent(
                `Hi, I want to order:\n${items.map((i) => `- ${i.name} (${(i.price * (i.quantity || 1))} ₪)`).join('\n')}\nTotal: ${total} ₪\nPayment: Visa / Mastercard`
              )}`}
              className="cart-panel-order cart-panel-pay-visa"
              target="_blank"
              rel="noopener noreferrer"
              onClick={onClose}
            >
              <i className="bi bi-credit-card-2-front" />
              <span>{t('cart.payVisa')}</span>
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
