/**
 * Hero — full-viewport hero section with logo, tagline, and Discover CTA.
 */

import { useLanguage } from '../context/LanguageContext';

export function Hero() {
  const { t } = useLanguage();

  return (
    <section className="hero-full" id="hero">
      <div className="hero-bg" />
      <div className="hero-content">
        <img
          src="/img/logo.webp"
          alt="Chef Farah Ammar"
          className="hero-logo anim-fade-up"
          width="400"
          height="200"
          decoding="async"
          fetchpriority="high"
        />
        <p className="hero-tagline anim-fade-up">{t('hero.tagline')}</p>
        <a href="#product" className="hero-cta anim-fade-up">
          {t('hero.cta')}
        </a>
      </div>
      <div className="hero-scroll anim-fade">
        <span>{t('hero.scroll')}</span>
        <i className="bi bi-chevron-down" />
      </div>
    </section>
  );
}
