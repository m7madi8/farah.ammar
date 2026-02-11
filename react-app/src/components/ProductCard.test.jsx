/**
 * ProductCard component tests — render, add to cart, link for product with detail page.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { LanguageProvider } from '../context/LanguageContext';
import { CartProvider } from '../context/CartContext';
import { ProductCard } from './ProductCard';

function wrap(ui) {
  return (
    <MemoryRouter>
      <LanguageProvider>
        <CartProvider>
          {ui}
        </CartProvider>
      </LanguageProvider>
    </MemoryRouter>
  );
}

const mockProduct = {
  id: '1',
  slug: 'dumplings-chicken',
  name: 'Dumplings – Chicken',
  nameAr: 'دامبلنغ – دجاج',
  description: 'Handcrafted chicken dumplings.',
  descriptionAr: 'دامبلنغ دجاج.',
  price: 25,
  category: 'boxes',
  imageUrl: '/img/1.webp',
  order: 1,
  badge: 'Signature',
};

describe('ProductCard', () => {
  it('renders product name and price', () => {
    render(wrap(<ProductCard product={mockProduct} />));
    expect(screen.getByText(/Dumplings – Chicken/)).toBeInTheDocument();
    expect(screen.getByText('25')).toBeInTheDocument();
  });

  it('has add to cart button', () => {
    render(wrap(<ProductCard product={mockProduct} />));
    const btn = screen.getByRole('button', { name: /add to cart/i });
    expect(btn).toBeInTheDocument();
  });

  it('calls onShowToast when add to cart is clicked', () => {
    const onShowToast = vi.fn();
    render(wrap(<ProductCard product={mockProduct} onShowToast={onShowToast} />));
    const btn = screen.getByRole('button', { name: /add to cart/i });
    fireEvent.click(btn);
    expect(onShowToast).toHaveBeenCalled();
  });

  it('links to product page when slug has detail page', () => {
    render(wrap(<ProductCard product={mockProduct} />));
    const link = screen.getByRole('link', { name: /view product/i });
    expect(link).toHaveAttribute('href', '/product/dumplings-chicken');
  });

  it('does not show view product link for no-detail slugs', () => {
    const sauce = { ...mockProduct, slug: 'teriyaki-sauce', name: 'Teriyaki' };
    render(wrap(<ProductCard product={sauce} />));
    expect(screen.queryByRole('link', { name: /view product/i })).not.toBeInTheDocument();
  });
});
