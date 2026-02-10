/**
 * Footer — site footer with Instagram link and copyright.
 */

import { useLanguage } from '../context/LanguageContext';

export function Footer() {
  const { t } = useLanguage();
  const year = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <a
          href="https://instagram.com/cheffarahammar"
          className="footer-instagram"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Instagram"
        >
          <i className="bi bi-instagram" aria-hidden="true" />
          <span>{t('footer.instagram')}</span>
        </a>
        <p className="footer-copy">
          © {year} {t('footer.copy')}
        </p>
      </div>
    </footer>
  );
}
