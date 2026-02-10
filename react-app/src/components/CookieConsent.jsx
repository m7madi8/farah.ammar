/**
 * CookieConsent — bottom bar for cookie notice; Accept / Ignore.
 */

import { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';

const STORAGE_KEY = 'farah-cookie-consent';

export function CookieConsent() {
  const { t } = useLanguage();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    try {
      if (!localStorage.getItem(STORAGE_KEY)) {
        const tmr = setTimeout(() => setVisible(true), 800);
        return () => clearTimeout(tmr);
      }
    } catch {}
  }, []);

  const accept = () => {
    try {
      localStorage.setItem(STORAGE_KEY, 'accepted');
    } catch {}
    setVisible(false);
  };

  const ignore = () => {
    try {
      localStorage.setItem(STORAGE_KEY, 'dismissed');
    } catch {}
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div
      className="cookie-consent cookie-consent-visible"
      aria-live="polite"
    >
      <div className="cookie-consent-inner">
        <span className="cookie-consent-icon" aria-hidden="true">
          <i className="bi bi-cookie" />
        </span>
        <p className="cookie-consent-msg">{t('cookie.msg')}</p>
        <div className="cookie-consent-btns">
          <button
            type="button"
            className="cookie-consent-btn cookie-consent-ignore"
            onClick={ignore}
          >
            {t('cookie.ignore')}
          </button>
          <button type="button" className="cookie-consent-btn" onClick={accept}>
            {t('cookie.accept')}
          </button>
        </div>
      </div>
    </div>
  );
}
