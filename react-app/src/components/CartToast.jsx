/**
 * CartToast — brief "Added to cart!" message shown after adding a product.
 */

import { useEffect, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';

export function CartToast({ show, onHide }) {
  const { t } = useLanguage();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setVisible(true);
      const tmr = setTimeout(() => {
        setVisible(false);
        onHide?.();
      }, 2200);
      return () => clearTimeout(tmr);
    }
  }, [show, onHide]);

  return (
    <div
      className={`cart-toast ${visible ? 'cart-toast-show' : ''}`}
      role="status"
      aria-live="polite"
      aria-hidden={!visible}
    >
      <i className="bi bi-check-circle-fill cart-toast-icon" />
      <span className="cart-toast-text">{t('cart.added')}</span>
    </div>
  );
}
