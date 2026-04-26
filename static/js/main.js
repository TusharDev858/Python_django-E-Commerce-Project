/* LuxeMarket — main.js */

// ── CSRF ──────────────────────────────────────────────
function csrfToken() {
  return document.cookie.split(';')
    .find(c => c.trim().startsWith('csrftoken='))?.split('=')[1] || '';
}

// ── THEME ──────────────────────────────────────────────
function getTheme() {
  return localStorage.getItem('lm-theme') ||
    (window.matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light');
}
function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('lm-theme', t);
  document.querySelectorAll('.ti-sun').forEach(el => el.style.display = t === 'dark' ? 'block' : 'none');
  document.querySelectorAll('.ti-moon').forEach(el => el.style.display = t === 'dark' ? 'none' : 'block');
}
function toggleTheme() { applyTheme(getTheme() === 'dark' ? 'light' : 'dark'); }

// ── TOAST ──────────────────────────────────────────────
function showToast(text, type = 'success') {
  let wrap = document.getElementById('toast-wrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.id = 'toast-wrap';
    wrap.className = 'toast-wrap';
    document.body.appendChild(wrap);
  }
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${text}</span>
    <button class="toast-close" onclick="dismissToast(this.parentElement)">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" width="13" height="13">
        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>`;
  wrap.appendChild(t);
  setTimeout(() => dismissToast(t), 5000);
}
function dismissToast(el) {
  if (!el || !el.isConnected) return;
  el.style.transition = 'opacity .28s,transform .28s';
  el.style.opacity = '0';
  el.style.transform = 'translateX(20px)';
  setTimeout(() => el.remove(), 300);
}

// ── CART DRAWER ────────────────────────────────────────
const $ = id => document.getElementById(id);

function openDrawer() {
  $('cart-drawer')?.classList.add('open');
  $('drawer-overlay')?.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeDrawer() {
  $('cart-drawer')?.classList.remove('open');
  $('drawer-overlay')?.classList.remove('open');
  document.body.style.overflow = '';
}

function updateCartBadge(count) {
  document.querySelectorAll('.nav-cart-count').forEach(el => el.textContent = count);
  const dc = $('drawer-count');
  if (dc) dc.textContent = count;
}

function renderDrawer(data) {
  const body  = $('drawer-items');
  const empty = $('drawer-empty');
  const foot  = $('drawer-foot');
  const total = $('drawer-total');
  if (!body) return;

  updateCartBadge(data.cart_count);

  if (!data.items || data.items.length === 0) {
    body.innerHTML = '';
    if (empty) empty.style.display = 'block';
    if (foot)  foot.style.display  = 'none';
    return;
  }
  if (empty) empty.style.display = 'none';
  if (foot)  foot.style.display  = 'block';
  if (total) total.textContent   = '$' + data.cart_total;

  body.innerHTML = data.items.map(item => `
    <div class="d-item" id="di-${item.id}">
      <div class="d-item-img">
        ${item.image
          ? `<img src="${item.image}" alt="${item.name}" />`
          : `<div class="d-item-emoji">📦</div>`}
      </div>
      <div class="d-item-info">
        <div class="d-item-name">${item.name}</div>
        <div class="d-item-meta">
          <span class="d-item-price">$${item.price}</span>
          <span class="d-item-qty">× ${item.quantity}</span>
        </div>
      </div>
      <span class="d-item-sub">$${item.subtotal}</span>
      <button class="d-item-rm" data-url="${item.remove_url}" title="Remove">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" width="13" height="13">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>`).join('');

  body.querySelectorAll('.d-item-rm').forEach(btn => {
    btn.addEventListener('click', async () => {
      const res = await fetch(btn.dataset.url, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest' }
      });
      if (res.ok) renderDrawer(await res.json());
    });
  });
}

// ── NOTIFICATION BELL ──────────────────────────────────
function updateNotifBadge(count) {
  const dot = $('notif-dot');
  if (!dot) return;
  dot.textContent = count;
  dot.classList.toggle('hide', count === 0);
  $('notif-btn')?.classList.toggle('ringing', count > 0);
}
window.updateNotifBadge = updateNotifBadge;

async function pollUnread() {
  try {
    const res = await fetch('/api/unread/');
    if (res.ok) updateNotifBadge((await res.json()).unread);
  } catch { /* ignore */ }
}

// ── MAIN ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  applyTheme(getTheme());

  // Navbar scroll shadow
  const nav = document.querySelector('.navbar');
  if (nav) window.addEventListener('scroll', () =>
    nav.classList.toggle('scrolled', scrollY > 18), { passive: true });

  // Mobile menu
  const hbg    = $('hamburger');
  const mobile = $('mobile-menu');
  if (hbg && mobile) {
    hbg.addEventListener('click', () => {
      const open = mobile.classList.toggle('open');
      hbg.setAttribute('aria-expanded', open);
    });
    document.addEventListener('click', e => {
      if (!hbg.contains(e.target) && !mobile.contains(e.target))
        mobile.classList.remove('open');
    });
  }

  // Cart drawer
  $('drawer-toggle')?.addEventListener('click', openDrawer);
  $('drawer-close')?.addEventListener('click', closeDrawer);
  $('drawer-overlay')?.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', e => e.key === 'Escape' && closeDrawer());

  // Load initial cart data into drawer
  if ($('cart-drawer')) {
    fetch('/api/cart-data/')
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) renderDrawer(d); })
      .catch(() => {});
  }

  // AJAX add-to-cart
  document.querySelectorAll('form[data-ajax-cart]').forEach(form => {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      try {
        const res = await fetch(form.action, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (res.ok) {
          const data = await res.json();
          renderDrawer(data);
          openDrawer();
          showToast(`"${data.product_name}" added to cart ✓`, 'success');
        }
      } catch { showToast('Could not add to cart', 'error'); }
    });
  });

  // Notification bell
  const notifBtn   = $('notif-btn');
  const notifPanel = $('notif-panel');
  if (notifBtn && notifPanel) {
    notifBtn.addEventListener('click', e => {
      e.stopPropagation();
      const open = notifPanel.classList.toggle('open');
      notifBtn.setAttribute('aria-expanded', open);
    });
    document.addEventListener('click', e => {
      if (!notifBtn.contains(e.target) && !notifPanel.contains(e.target))
        notifPanel.classList.remove('open');
    });
    pollUnread();
    setInterval(pollUnread, 30000);
  }

  // Auto-dismiss Django messages
  document.querySelectorAll('.toast').forEach(t => {
    t.querySelector('.toast-close')?.addEventListener('click', () => dismissToast(t));
    setTimeout(() => dismissToast(t), 5000);
  });

  // Image preview on product form
  const imgInput = $('id_image');
  const imgEl    = $('img-preview-el');
  const imgPh    = $('img-preview-ph');
  if (imgInput && imgEl) {
    imgInput.addEventListener('change', e => {
      const file = e.target.files[0];
      if (!file) return;
      const r = new FileReader();
      r.onload = ev => {
        imgEl.src = ev.target.result;
        imgEl.style.display = 'block';
        if (imgPh) imgPh.style.display = 'none';
      };
      r.readAsDataURL(file);
    });
  }

  // Cart page qty buttons
  document.querySelectorAll('.qty-form').forEach(form => {
    const inp   = form.querySelector('.qty-input');
    const minus = form.querySelector('.qty-minus');
    const plus  = form.querySelector('.qty-plus');
    if (!inp) return;
    minus?.addEventListener('click', () => { inp.value = Math.max(0, +inp.value - 1); form.submit(); });
    plus?.addEventListener ('click', () => { inp.value = +inp.value + 1; form.submit(); });
  });

  // Scroll-triggered animations
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.animationPlayState = 'running';
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    document.querySelectorAll('.product-card').forEach((card, i) => {
      card.style.animationDelay = `${i * 0.07}s`;
      card.style.animationPlayState = 'paused';
      io.observe(card);
    });
  }
});
