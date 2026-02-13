/**
 * SwipeIcon — Lordicon-style wired outline swipe left-right animation.
 * Inspired by https://lordicon.com/icons/wired/outline/1444-swipe-left-right
 * Colors customized to match site theme (lavender, deep-purple).
 */
export function SwipeIcon({ className = '', width = 48, height = 48 }) {
  return (
    <span
      className={`shop-swipe-icon-wrap ${className}`}
      role="img"
      aria-hidden="true"
      style={{ display: 'inline-block', width, height }}
    >
      <svg
        width={width}
        height={height}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shop-swipe-icon-svg"
      >
        <path
          d="M18 24H6M42 24H30"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          className="swipe-line"
        />
        <path
          d="M12 18L6 24L12 30"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="swipe-arrow-left"
        />
        <path
          d="M36 18L42 24L36 30"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="swipe-arrow-right"
        />
      </svg>
    </span>
  );
}
