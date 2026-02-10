/**
 * LanguageContext — global state for locale (en / ar) and translations.
 * Used by Navbar, Footer, and all pages for i18n.
 */

import { createContext, useContext, useState, useEffect } from 'react';
import { translations } from '../data/translations';

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [lang, setLangState] = useState(() => {
    try {
      const s = localStorage.getItem('farah-lang');
      return s === 'ar' || s === 'en' ? s : 'en';
    } catch {
      return 'en';
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('farah-lang', lang);
    } catch {}
    const root = document.getElementById('htmlRoot');
    if (root) {
      root.lang = lang;
      root.dir = lang === 'ar' ? 'rtl' : 'ltr';
    }
  }, [lang]);

  const t = (key) => (translations[lang] || translations.en)[key] ?? key;
  const toggleLang = () => setLangState((prev) => (prev === 'ar' ? 'en' : 'ar'));

  return (
    <LanguageContext.Provider value={{ lang, t, toggleLang }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error('useLanguage must be used within LanguageProvider');
  return ctx;
}
