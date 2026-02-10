/**
 * ProductCard — single product preview card for the shop grid.
 * Shows image, title, price, description; "View product" link only for products with a detail page.
 * Products in NO_DETAIL_PAGE_SLUGS have no product page — card links nowhere, only Add to cart.
 */

import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { useCart } from '../context/CartContext';
import { NO_DETAIL_PAGE_SLUGS } from '../constants/products';

export function ProductCard({ product, onShowToast }) {
  const { t, lang } = useLanguage();
  const { addItem } = useCart();
  const hasDetailPage = !NO_DETAIL_PAGE_SLUGS.includes(product.slug);

  const name = lang === 'ar' && product.nameAr ? product.nameAr : product.name;
  const desc = lang === 'ar' && product.descriptionAr ? product.descriptionAr : product.description;
  const badgeKey = product.badge === 'Sauce' ? 'product.badgeSauce' : product.badge === 'Accessory' ? 'product.badgeAccessory' : 'product.badge';
  const badge = t(badgeKey);

  const handleAddToCart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    addItem({ ...product, name });
    onShowToast?.();
  };

  const cardContent = (
    <>
      <div className="product-preview-image">
        <img
          src={product.imageUrl}
          alt={name}
          width="400"
          height="300"
          loading="lazy"
          decoding="async"
        />
        <span className="product-preview-badge">{badge}</span>
      </div>
      <div className="product-preview-body">
        <h3 className="product-preview-title">{name}</h3>
        <div className="product-preview-price-wrap">
          <span className="product-preview-price">{product.price}</span>
          <span className="product-preview-currency">₪</span>
        </div>
        <p className={`product-preview-desc ${product.slug === 'chop-sticks' ? 'product-preview-chop-note' : ''}`}>
          {desc}
        </p>
        {hasDetailPage && (
          <span className="product-preview-cta">
            {t('product.viewProduct')}
            <i className="bi bi-arrow-right" aria-hidden="true" />
          </span>
        )}
      </div>
    </>
  );

  return (
    <div
      className="product-preview product-preview-card anim-on-scroll"
      data-category={product.category}
      data-price={product.price}
      data-order={product.order}
    >
      {hasDetailPage ? (
        <Link to={`/product/${product.slug}`} className="product-preview-link">
          {cardContent}
        </Link>
      ) : (
        <div className="product-preview-link product-preview-link--no-page">
          {cardContent}
        </div>
      )}
      <button
        type="button"
        className="product-preview-add-cart"
        onClick={handleAddToCart}
      >
        <i className="bi bi-cart-plus" />
        <span>{t('product.addToCart')}</span>
      </button>
    </div>
  );
}
