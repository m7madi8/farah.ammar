/**
 * OrderSummary — displays list of cart items and total for checkout page.
 * Used inside CheckoutPage; receives items and total from CartContext.
 */

import { useLanguage } from '../context/LanguageContext';

export function OrderSummary({ items, total }) {
  const { t } = useLanguage();

  return (
    <section className="checkout-summary" aria-labelledby="summaryHeading">
      <h2 id="summaryHeading" className="checkout-summary-title">
        {t('checkout.orderSummary')}
      </h2>
      <ul className="checkout-summary-list">
        {items.map((item, i) => (
          <li key={`${item.productId}-${i}`} className="checkout-summary-item">
            <span className="checkout-summary-name">{item.name}</span>
            <span className="checkout-summary-price">
              {(item.price * (item.quantity || 1))} ₪
            </span>
          </li>
        ))}
      </ul>
      <div className="checkout-summary-total">
        <span>{t('cart.total')}</span>
        <span>{total} ₪</span>
      </div>
    </section>
  );
}
