/**
 * Hero — full-viewport hero section with logo, tagline, and Discover CTA.
 */

import { useLanguage } from '../context/LanguageContext';
import { HeroBackground } from './HeroBackground';

export function Hero() {
  const { t } = useLanguage();
  const tagline = t('hero.tagline');

  const parts = tagline.split(/(\s+)/).filter(Boolean);
  const delayPerUnit = 0.12;

  return (
    <section className="hero-full" id="hero">
      <div className="hero-bg">
        <HeroBackground />
      </div>
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
        <p className="hero-tagline hero-tagline-type" aria-label={tagline}>
          {parts.map((part, i) => (
            <span
              key={i}
              className="hero-tagline-char"
              style={{ animationDelay: `${0.5 + i * delayPerUnit}s` }}
            >
              {part === ' ' ? '\u00A0' : part}
            </span>
          ))}
        </p>
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
