/* Farah Ammar — Cart */
(function () {
  var STORAGE_KEY = 'farah-cart';
  var WA_NUMBER = '972501234567';

  function getCart() {
    try {
      var s = localStorage.getItem(STORAGE_KEY);
      return s ? JSON.parse(s) : [];
    } catch (e) {
      return [];
    }
  }

  function saveCart(items) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch (e) {}
    updateUI();
  }

  function addToCart(name, price) {
    var cart = getCart();
    cart.push({ name: name, price: parseInt(price, 10) });
    saveCart(cart);
    showAddedToast();
    animateCartBadge();
  }

  function showAddedToast() {
    var toast = document.getElementById('cartToast');
    if (!toast) return;
    var text = toast.querySelector('.cart-toast-text');
    if (text && window.getTranslation) text.textContent = window.getTranslation('cart.added');
    toast.classList.remove('cart-toast-show');
    toast.setAttribute('aria-hidden', 'false');
    void toast.offsetWidth;
    toast.classList.add('cart-toast-show');
    clearTimeout(window.cartToastTimer);
    window.cartToastTimer = setTimeout(function () {
      toast.classList.remove('cart-toast-show');
      toast.setAttribute('aria-hidden', 'true');
    }, 2200);
  }

  function animateCartBadge() {
    var badge = document.getElementById('cartBadge');
    if (badge && badge.getAttribute('aria-hidden') !== 'true') {
      badge.classList.remove('cart-badge-pop');
      void badge.offsetWidth;
      badge.classList.add('cart-badge-pop');
      setTimeout(function () { badge.classList.remove('cart-badge-pop'); }, 400);
    }
    var cartBtn = document.getElementById('navCart');
    if (cartBtn) {
      cartBtn.classList.remove('cart-icon-bounce');
      void cartBtn.offsetWidth;
      cartBtn.classList.add('cart-icon-bounce');
      setTimeout(function () { cartBtn.classList.remove('cart-icon-bounce'); }, 500);
    }
  }

  function removeFromCart(index) {
    var cart = getCart();
    cart.splice(index, 1);
    saveCart(cart);
  }

  function getTotal() {
    return getCart().reduce(function (sum, item) { return sum + item.price; }, 0);
  }

  function buildWaMessage(paymentMethod) {
    var cart = getCart();
    var lines = ['Hi, I want to order:'];
    cart.forEach(function (item) {
      lines.push('- ' + item.name + ' (' + item.price + ' ₪)');
    });
    lines.push('Total: ' + getTotal() + ' ₪');
    if (paymentMethod) {
      lines.push('Payment: ' + paymentMethod);
    }
    return encodeURIComponent(lines.join('\n'));
  }

  function renderCart() {
    var list = document.getElementById('cartList');
    var empty = document.getElementById('cartEmpty');
    var footer = document.getElementById('cartFooter');
    var badge = document.getElementById('cartBadge');
    var totalEl = document.getElementById('cartTotal');

    if (!list) return;

    var cart = getCart();
    var count = cart.length;

    if (badge) {
      badge.textContent = count;
      badge.setAttribute('aria-hidden', count === 0 ? 'true' : 'false');
    }

    if (count === 0) {
      if (empty) empty.hidden = false;
      if (footer) footer.hidden = true;
      list.innerHTML = '';
      return;
    }

    if (empty) empty.hidden = true;
    if (footer) footer.hidden = false;
    if (totalEl) totalEl.textContent = getTotal() + ' ₪';

    var removeLabel = (window.getTranslation && window.getTranslation('cart.remove')) || 'Delete';
    list.innerHTML = cart.map(function (item, i) {
      return '<div class="cart-item" data-index="' + i + '">' +
        '<span class="cart-item-name">' + escapeHtml(item.name) + '</span>' +
        '<span class="cart-item-price">' + item.price + ' ₪</span>' +
        '<button type="button" class="cart-item-remove" aria-label="' + escapeHtml(removeLabel) + '" data-index="' + i + '">' + escapeHtml(removeLabel) + '</button>' +
        '</div>';
    }).join('');

    list.querySelectorAll('.cart-item-remove').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var idx = parseInt(btn.getAttribute('data-index'), 10);
        removeFromCart(idx);
      });
    });
  }

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function updateUI() {
    renderCart();
  }

  function openCart() {
    var panel = document.getElementById('cartPanel');
    var btn = document.getElementById('navCart');
    if (panel && btn) {
      panel.classList.add('cart-panel-open');
      panel.setAttribute('aria-hidden', 'false');
      btn.setAttribute('aria-expanded', 'true');
    }
  }

  function closeCart() {
    var panel = document.getElementById('cartPanel');
    var btn = document.getElementById('navCart');
    if (panel && btn) {
      panel.classList.remove('cart-panel-open');
      panel.setAttribute('aria-hidden', 'true');
      btn.setAttribute('aria-expanded', 'false');
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    renderCart();

    document.querySelectorAll('.product-preview-add-cart').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var name = btn.getAttribute('data-cart-name') || '';
        var price = btn.getAttribute('data-cart-price') || '0';
        addToCart(name, price);
      });
    });

    var cartBtn = document.getElementById('navCart');
    var cartClose = document.getElementById('cartClose');
    var cartOrderBtn = document.getElementById('cartOrderBtn');

    if (cartBtn) {
      cartBtn.addEventListener('click', function () {
        if (!document.getElementById('cartPanel').classList.contains('cart-panel-open')) {
          openCart();
        } else {
          closeCart();
        }
      });
    }

    if (cartClose) {
      cartClose.addEventListener('click', closeCart);
    }

    if (cartOrderBtn) {
      cartOrderBtn.addEventListener('click', function (e) {
        e.preventDefault();
        var cart = getCart();
        if (cart.length === 0) return;
        var url = 'https://wa.me/' + WA_NUMBER + '?text=' + buildWaMessage('Cash on delivery');
        window.open(url, '_blank', 'noopener');
      });
    }

    var cartPayVisaBtn = document.getElementById('cartPayVisaBtn');
    if (cartPayVisaBtn) {
      cartPayVisaBtn.addEventListener('click', function (e) {
        e.preventDefault();
        var cart = getCart();
        if (cart.length === 0) return;
        var url = 'https://wa.me/' + WA_NUMBER + '?text=' + buildWaMessage('Visa / Mastercard');
        window.open(url, '_blank', 'noopener');
      });
    }

    document.addEventListener('click', function (e) {
      var panel = document.getElementById('cartPanel');
      var cartBtn = document.getElementById('navCart');
      if (!panel || !cartBtn || !panel.classList.contains('cart-panel-open')) return;
      if (!panel.contains(e.target) && !cartBtn.contains(e.target)) {
        closeCart();
      }
    });
  });
})();
