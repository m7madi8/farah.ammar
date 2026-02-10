(function () {
  var ORDERS_KEY = 'farah-orders';

  function getOrders() {
    try {
      var s = localStorage.getItem(ORDERS_KEY);
      return s ? JSON.parse(s) : [];
    } catch (e) {
      return [];
    }
  }

  function saveOrders(orders) {
    try {
      localStorage.setItem(ORDERS_KEY, JSON.stringify(orders));
    } catch (e) {}
  }

  function formatDate(iso) {
    try {
      var d = new Date(iso);
      return d.toLocaleDateString('ar-EG', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return iso || '';
    }
  }

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text == null ? '' : text;
    return div.innerHTML;
  }

  function renderOrders() {
    var orders = getOrders();
    var listEl = document.getElementById('ordersList');
    var emptyEl = document.getElementById('ordersEmpty');
    var statTotal = document.getElementById('statTotal');
    var statPending = document.getElementById('statPending');
    var statDone = document.getElementById('statDone');

    var pendingCount = orders.filter(function (o) { return o.status !== 'done'; }).length;
    var doneCount = orders.filter(function (o) { return o.status === 'done'; }).length;

    if (statTotal) statTotal.textContent = orders.length;
    if (statPending) statPending.textContent = pendingCount;
    if (statDone) statDone.textContent = doneCount;

    if (orders.length === 0) {
      if (emptyEl) emptyEl.style.display = '';
      var cards = listEl ? listEl.querySelectorAll('.order-card') : [];
      cards.forEach(function (c) { c.remove(); });
      return;
    }

    if (emptyEl) emptyEl.style.display = 'none';

    var existingCards = listEl ? listEl.querySelectorAll('.order-card') : [];
    existingCards.forEach(function (c) { c.remove(); });

    orders.forEach(function (order) {
      var card = document.createElement('div');
      card.className = 'order-card';
      card.setAttribute('data-status', order.status || 'pending');
      card.setAttribute('data-id', order.id || '');

      var itemsHtml = (order.items || []).map(function (item) {
        return '<div class="order-row"><i class="bi bi-dot"></i><span>' + escapeHtml(item.name) + ' — ' + (item.price || 0) + ' ₪</span></div>';
      }).join('');

      var badgeClass = (order.status === 'done') ? 'order-badge order-badge-done' : 'order-badge order-badge-pending';
      var badgeText = (order.status === 'done') ? 'تم التوصيل' : 'قيد الانتظار';

      card.innerHTML =
        '<div class="order-card-header">' +
          '<span class="order-id">' + escapeHtml(order.id || '') + '</span>' +
          '<span class="order-date">' + escapeHtml(formatDate(order.date)) + '</span>' +
          '<span class="' + badgeClass + '">' + badgeText + '</span>' +
          ((order.status !== 'done') ? '<button type="button" class="order-btn-done" data-id="' + escapeHtml(order.id || '') + '" title="تم التوصيل"><i class="bi bi-check-circle"></i> تم التوصيل</button>' : '') +
        '</div>' +
        '<div class="order-card-body">' +
          '<div class="order-row"><i class="bi bi-person"></i><span>' + escapeHtml(order.name || '') + '</span></div>' +
          '<div class="order-row"><i class="bi bi-telephone"></i><a href="tel:' + escapeHtml(order.phone || '') + '">' + escapeHtml(order.phone || '') + '</a></div>' +
          '<div class="order-row"><i class="bi bi-geo-alt"></i><span>' + escapeHtml((order.address || '').replace(/\n/g, ' ')) + '</span></div>' +
          '<div class="order-payment" style="margin-top:0.75rem;"><strong>الطلب:</strong></div>' +
          itemsHtml +
          '<div class="order-row" style="margin-top:0.5rem;"><strong>المجموع: ' + (order.total || 0) + ' ₪</strong></div>' +
          (order.notes ? '<p class="order-notes">ملاحظات: ' + escapeHtml(order.notes) + '</p>' : '') +
          '<div class="order-card-actions"><button type="button" class="order-btn-print" data-id="' + escapeHtml(order.id || '') + '" title="طباعة الفاتورة"><i class="bi bi-printer"></i> طباعة الفاتورة</button></div>' +
        '</div>';

      if (listEl) {
        listEl.insertBefore(card, listEl.firstChild || emptyEl);
      }

      var btnDone = card.querySelector('.order-btn-done');
      if (btnDone) {
        btnDone.addEventListener('click', function () {
          var id = btnDone.getAttribute('data-id');
          var list = getOrders();
          var idx = list.findIndex(function (o) { return o.id === id; });
          if (idx !== -1) {
            list[idx].status = 'done';
            saveOrders(list);
            renderOrders();
          }
        });
      }

      var btnPrint = card.querySelector('.order-btn-print');
      if (btnPrint) {
        btnPrint.addEventListener('click', function () {
          printOrderInvoice(order);
        });
      }
    });
  }

  function printOrderInvoice(order) {
    var dateStr = formatDate(order.date);
    var itemsRows = (order.items || []).map(function (item) {
      return '<tr><td>' + escapeHtml(item.name) + '</td><td style="text-align:center">' + (item.price || 0) + ' &#8362;</td></tr>';
    }).join('');
    var statusText = order.status === 'done' ? '\u062a\u0645 \u0627\u0644\u062a\u0648\u0635\u064a\u0644' : '\u0642\u064a\u062f \u0627\u0644\u0627\u0646\u062a\u0638\u0627\u0631';
    var notesPart = order.notes ? '<p style="margin-top:1rem;font-size:0.9rem"><strong>\u0645\u0644\u0627\u062d\u0638\u0627\u062a:</strong> ' + escapeHtml(order.notes) + '</p>' : '';
    var footerText = '\u0634\u0643\u0631\u0627\u064b \u0644\u0637\u0644\u0628\u0643 \u2014 Chef Farah Ammar';
    var invoiceHtml = '<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>\u0641\u0627\u062a\u0648\u0631\u0629 ' + escapeHtml(order.id || '') + '</title><style>' +
      '*{box-sizing:border-box}body{font-family:Segoe UI,Tahoma,Arial,sans-serif;margin:0;padding:2rem;color:#1a1520;font-size:14px}' +
      '.inv-header{text-align:center;margin-bottom:2rem;padding-bottom:1rem;border-bottom:2px solid #2D0B59}' +
      '.inv-title{font-size:1.5rem;font-weight:700;color:#2D0B59;margin:0 0 0.25rem}' +
      '.inv-sub{font-size:0.9rem;color:#5c5466;margin:0}' +
      '.inv-meta{margin-bottom:1.5rem;display:flex;justify-content:space-between;flex-wrap:wrap;gap:1rem}' +
      '.inv-meta p{margin:0 0 0.35rem;font-size:0.95rem}' +
      '.inv-table{width:100%;border-collapse:collapse;margin:1rem 0}' +
      '.inv-table th,.inv-table td{padding:0.5rem 0.75rem;text-align:right;border:1px solid #ddd}' +
      '.inv-table th{background:#2D0B59;color:#fff;font-weight:600}' +
      '.inv-total{font-size:1.15rem;font-weight:700;margin-top:1rem;padding-top:0.75rem;border-top:2px solid #2D0B59}' +
      '.inv-footer{margin-top:2rem;padding-top:1rem;font-size:0.85rem;color:#5c5466;text-align:center}' +
      '@media print{body{padding:1rem}}' +
      '</style></head><body>' +
      '<div class="inv-header"><h1 class="inv-title">Chef Farah Ammar</h1><p class="inv-sub">\u0641\u0627\u062a\u0648\u0631\u0629 \u0637\u0644\u0628 \u2014 \u062f\u0641\u0639 \u0639\u0646\u062f \u0627\u0644\u0627\u0633\u062a\u0644\u0627\u0645</p></div>' +
      '<div class="inv-meta">' +
        '<div><p><strong>\u0631\u0642\u0645 \u0627\u0644\u0637\u0644\u0628:</strong> ' + escapeHtml(order.id || '') + '</p><p><strong>\u0627\u0644\u062a\u0627\u0631\u064a\u062e:</strong> ' + escapeHtml(dateStr) + '</p><p><strong>\u0627\u0644\u062d\u0627\u0644\u0629:</strong> ' + statusText + '</p></div>' +
        '<div><p><strong>\u0627\u0644\u0639\u0645\u064a\u0644:</strong> ' + escapeHtml(order.name || '') + '</p><p><strong>\u0627\u0644\u0647\u0627\u062a\u0641:</strong> ' + escapeHtml(order.phone || '') + '</p><p><strong>\u0627\u0644\u0639\u0646\u0648\u0627\u0646:</strong> ' + escapeHtml((order.address || '').replace(/\n/g, ' ')) + '</p></div>' +
      '</div>' +
      '<table class="inv-table"><thead><tr><th>\u0627\u0644\u0635\u0646\u0641</th><th style="width:100px">\u0627\u0644\u0633\u0639\u0631</th></tr></thead><tbody>' + itemsRows + '</tbody></table>' +
      '<div class="inv-total">\u0627\u0644\u0645\u062c\u0645\u0648\u0639: ' + (order.total || 0) + ' &#8362;</div>' +
      notesPart +
      '<div class="inv-footer">' + footerText + '</div>' +
      '</body></html>';
    var w = window.open('', '_blank', 'width=700,height=800');
    if (w) {
      w.document.write(invoiceHtml);
      w.document.close();
      w.focus();
      setTimeout(function () {
        try {
          w.print();
          if (w.onafterprint !== undefined) {
            w.onafterprint = function () { w.close(); };
          } else {
            setTimeout(function () { w.close(); }, 500);
          }
        } catch (err) {
          w.close();
        }
      }, 300);
    }
  }

  var toggle = document.getElementById('sidebarToggle');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');
  if (toggle) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('sidebar-open');
      overlay.classList.toggle('show');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', function () {
      sidebar.classList.remove('sidebar-open');
      overlay.classList.remove('show');
    });
  }

  renderOrders();
})();
