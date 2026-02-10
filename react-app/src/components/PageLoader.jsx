/**
 * PageLoader — full-screen loading overlay with logo and bar, hidden when app is ready.
 */

export function PageLoader({ visible }) {
  if (!visible) return null;
  return (
    <div className="page-loader" id="pageLoader">
      <div className="loader-inner">
        <img
          src="/img/logo.png"
          alt="Chef Farah Ammar"
          className="loader-logo"
          width="220"
          height="110"
          decoding="async"
        />
        <div className="loader-bar">
          <span className="loader-bar-fill" />
        </div>
      </div>
    </div>
  );
}
