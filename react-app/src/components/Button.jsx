/**
 * Button — reusable button/link with variants (primary, outline, pay, cod).
 * Used for CTAs, form submit, and product actions.
 */

export function Button({
  children,
  type = 'button',
  variant = 'primary',
  className = '',
  as: Component = 'button',
  ...props
}) {
  const base = 'btn-checkout-submit';
  const variants = {
    primary: '',
    outline: 'cookie-consent-ignore',
    pay: 'product-btn product-btn-pay',
    cod: 'product-btn product-btn-cod',
    cart: 'product-btn product-btn-cart',
  };
  const cls = [base, variants[variant], className].filter(Boolean).join(' ');
  return (
    <Component type={Component === 'button' ? type : undefined} className={cls} {...props}>
      {children}
    </Component>
  );
}
