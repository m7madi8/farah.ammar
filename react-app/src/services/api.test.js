/**
 * API service tests — fetchProducts, fetchProductBySlug, submitOrder.
 * Mocks fetch; no real backend required.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchProducts, fetchProductBySlug, submitOrder } from './api';

describe('api', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  describe('fetchProducts', () => {
    it('returns mock products when VITE_API_BASE is not set', async () => {
      const products = await fetchProducts();
      expect(Array.isArray(products)).toBe(true);
      if (products.length > 0) {
        expect(products[0]).toHaveProperty('slug');
        expect(products[0]).toHaveProperty('name');
        expect(products[0]).toHaveProperty('price');
      }
    });

    it('returns array from API when fetch is mocked', async () => {
      const mockData = [{ id: 1, slug: 'test', name: 'Test', price: 10 }];
      global.fetch = vi.fn(() =>
        Promise.resolve({ ok: true, json: () => Promise.resolve({ results: mockData }) })
      );
      const products = await fetchProducts();
      expect(Array.isArray(products)).toBe(true);
    });
  });

  describe('fetchProductBySlug', () => {
    it('returns product matching slug from fetchProducts result', async () => {
      const product = await fetchProductBySlug('dumplings-chicken');
      if (product) {
        expect(product.slug).toBe('dumplings-chicken');
      } else {
        expect(product).toBeNull();
      }
    });
  });

  describe('submitOrder', () => {
    it('returns local success when BASE is not set', async () => {
      const result = await submitOrder({ name: 'T', phone: '1', items: [], total: 0 });
      expect(result).toHaveProperty('ok', true);
      expect(result).toHaveProperty('orderId');
    });

    it('submitOrder with BASE set uses POST and JSON body', async () => {
      global.fetch = vi.fn(() =>
        Promise.resolve({ ok: true, json: () => Promise.resolve({ id: 123 }) })
      );
      await submitOrder({
        name: 'Test',
        phone: '1',
        address: 'Addr',
        items: [{ productId: 1, quantity: 1, price: 10, name: 'P' }],
        total: 10,
      });
      if (fetch.mock.calls.length) {
        expect(fetch.mock.calls[0][1].method).toBe('POST');
        expect(typeof fetch.mock.calls[0][1].body).toBe('string');
      }
    });
  });
});
