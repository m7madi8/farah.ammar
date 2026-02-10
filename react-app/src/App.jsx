/**
 * App — root component with React Router and global providers.
 * Routes: Home (/), Product detail (/product/:slug), Checkout (/checkout).
 * Cart panel state is lifted here so Navbar can open it from any page.
 */

import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext';
import { CartProvider } from './context/CartContext';
import { HomePage } from './pages/HomePage';
import { ProductDetailPage } from './pages/ProductDetailPage';
import { CheckoutPage } from './pages/CheckoutPage';

function AppRoutes() {
  const location = useLocation();
  const [cartOpen, setCartOpen] = useState(false);
  const toggleCart = () => setCartOpen((prev) => !prev);

  // Scroll to top when navigating to a new page (e.g. product page)
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  // Scroll to #product when hash is present (e.g. /#product)
  useEffect(() => {
    if (location.hash === '#product') {
      const el = document.getElementById('product');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  }, [location.pathname, location.hash]);

  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage cartOpen={cartOpen} onCartOpen={toggleCart} setCartOpen={setCartOpen} />} />
        <Route path="/product/:slug" element={<ProductDetailPage cartOpen={cartOpen} onCartOpen={toggleCart} setCartOpen={setCartOpen} />} />
        <Route path="/checkout" element={<CheckoutPage />} />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <LanguageProvider>
        <CartProvider>
          <AppRoutes />
        </CartProvider>
      </LanguageProvider>
    </BrowserRouter>
  );
}
