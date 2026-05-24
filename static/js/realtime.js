// =============================================
// Anas Aatar Wale — Real-Time Auto Updater
// Polls /api/realtime every 3 seconds
// Updates DOM without full page reload
// =============================================

const RT = {
  interval:  3000,
  lastTs:    0,
  _timer:    null,
  page:      document.body.dataset.page || 'index',

  start() {
    this._timer = setInterval(() => this.poll(), this.interval);
    this.poll(); // immediate first call
  },

  stop() { clearInterval(this._timer); },

  async poll() {
    try {
      const res  = await fetch('/api/realtime');
      const data = await res.json();
      if (data.ts === this.lastTs) return; // nothing changed
      this.lastTs = data.ts;
      this.applyUpdates(data);
    } catch(e) { /* silent fail — server may be restarting */ }
  },

  applyUpdates(data) {
    this.updateSettings(data.settings);
    this.updateProducts(data.products, data.featured, data.top_rated);
    this.updateCategories(data.categories);
    if (this.page === 'orders') this.pollOrders();
  },

  // ── Site Settings (hero text, logo, hero image) ──────
  updateSettings(s) {
    if (!s) return;

    // Hero title
    const heroTitle = document.getElementById('rtHeroTitle');
    if (heroTitle && heroTitle.innerHTML !== s.hero_title) {
      heroTitle.innerHTML = s.hero_title;
      heroTitle.classList.add('rt-flash');
      setTimeout(() => heroTitle.classList.remove('rt-flash'), 600);
    }

    // Hero subtitle
    const heroSub = document.getElementById('rtHeroSubtitle');
    if (heroSub && heroSub.textContent.trim() !== s.hero_subtitle.trim()) {
      heroSub.textContent = s.hero_subtitle;
      heroSub.classList.add('rt-flash');
      setTimeout(() => heroSub.classList.remove('rt-flash'), 600);
    }

    // Hero image
    if (s.hero_image) {
      const heroImg = document.getElementById('rtHeroImage');
      if (heroImg && heroImg.src !== s.hero_image && !heroImg.src.endsWith(s.hero_image.replace('/static/uploads/','').replace('/static/',''))) {
        heroImg.src = s.hero_image + '?t=' + Date.now();
      }
      const heroImgWrap = document.getElementById('rtHeroImageWrap');
      if (heroImgWrap) heroImgWrap.style.display = '';
    }

    // Logo
    if (s.logo_image) {
      document.querySelectorAll('.rt-logo-img').forEach(el => {
        el.src = s.logo_image + '?t=' + Date.now();
        el.style.display = '';
      });
      document.querySelectorAll('.rt-logo-emoji').forEach(el => el.style.display = 'none');
    }

    // Site name
    document.querySelectorAll('.rt-site-name').forEach(el => {
      if (el.textContent !== s.site_name) el.textContent = s.site_name;
    });
  },

  // ── Products ──────────────────────────────────────────
  updateProducts(products, featured, topRated) {
    if (!products) return;

    // Update individual product cards already on page
    products.forEach(p => {
      // Price
      document.querySelectorAll(`[data-rt-price="${p.id}"]`).forEach(el => {
        const newVal = '₹' + Math.round(p.price);
        if (el.textContent !== newVal) {
          el.textContent = newVal;
          this._flash(el);
        }
      });
      // Name
      document.querySelectorAll(`[data-rt-name="${p.id}"]`).forEach(el => {
        if (el.textContent !== p.name) { el.textContent = p.name; this._flash(el); }
      });
      // Stock
      document.querySelectorAll(`[data-rt-stock="${p.id}"]`).forEach(el => {
        const label = p.stock > 10 ? '✅ In Stock' : p.stock > 0 ? `⚡ Only ${p.stock} left` : '❌ Out of Stock';
        if (el.textContent.trim() !== label.trim()) { el.textContent = label; this._flash(el); }
      });
      // Image
      document.querySelectorAll(`[data-rt-img="${p.id}"]`).forEach(el => {
        if (p.image && el.src && !el.src.includes(p.image)) {
          el.src = p.image + '?t=' + Date.now();
        }
      });
    });

    // Re-render featured grid if on homepage
    const featuredGrid = document.getElementById('rtFeaturedGrid');
    if (featuredGrid && featured) {
      this._renderProductGrid(featuredGrid, featured);
    }
    const topGrid = document.getElementById('rtTopRatedGrid');
    if (topGrid && topRated) {
      this._renderProductGrid(topGrid, topRated);
    }

    // Products page full grid
    const productsGrid = document.getElementById('rtProductsGrid');
    if (productsGrid && products) {
      this._renderProductGrid(productsGrid, products);
    }
  },

  _renderProductGrid(container, products) {
    // Keep admin "+add" card if present
    const addCard = container.querySelector('.add-product-card');
    const isAdmin = document.body.dataset.admin === '1';

    const newHTML = products.map((p, i) => this._productCardHTML(p, i)).join('');
    const addHTML = isAdmin ? `<div class="product-card add-product-card" onclick="adminOpenAddProduct()">
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;min-height:280px;gap:10px;color:var(--text-light)">
        <div style="width:60px;height:60px;border-radius:50%;border:2.5px dashed var(--border);display:flex;align-items:center;justify-content:center;font-size:1.8rem">+</div>
        <span style="font-weight:600;font-size:0.9rem">Add Product</span>
      </div>
    </div>` : '';

    container.innerHTML = newHTML + addHTML;
  },

  _productCardHTML(p, i) {
    const emoji = this._emoji(p.name);
    const imgHTML = p.image
      ? `<img src="${p.image}" alt="${p.name}" style="width:100%;height:100%;object-fit:cover;transition:transform .5s" data-rt-img="${p.id}">`
      : `<div class="product-img-placeholder" style="font-size:4rem">${emoji}</div>`;
    const isAdmin = document.body.dataset.admin === '1';
    const threeDots = isAdmin ? `
      <div class="three-dots-menu" onclick="event.stopPropagation()">
        <button class="three-dots-btn" onclick="toggleDotMenu(this)">⋮</button>
        <div class="dot-menu-dropdown">
          <button onclick="adminEditProduct(${p.id})">✏️ Edit Product</button>
          <button onclick="adminEditProductImage(${p.id})">🖼️ Change Image</button>
          <button onclick="adminDeleteProduct(${p.id},'${p.name.replace(/'/g,"\\'")}')">🗑️ Delete</button>
        </div>
      </div>` : '';

    return `
    <div class="product-card" style="animation-delay:${i*0.06}s"
         onclick="window.location.href='/product/${p.id}'">
      <div class="product-img">
        ${imgHTML}
        <span class="product-badge"${i >= 3 ? ' style="display:none"' : ''}>⭐ Best Seller</span>
        <button class="product-wishlist-btn" onclick="event.stopPropagation();toggleWishlist(${p.id},this)">🤍</button>
        ${threeDots}
      </div>
      <div class="product-body">
        <div class="product-category">${p.category_name}</div>
        <div class="product-name" data-rt-name="${p.id}">${p.name}</div>
        <div class="product-rating">
          <span class="rating-stars">★★★★★</span>
          <span>${p.rating}</span>
          <span>• ${p.volume}</span>
        </div>
        <div class="product-footer">
          <div>
            <div class="product-price" data-rt-price="${p.id}">₹${Math.round(p.price)}</div>
            <div class="product-volume">${p.volume} attar</div>
          </div>
          <button class="btn-add-cart" onclick="event.stopPropagation();addToCart(${p.id})">+</button>
        </div>
      </div>
    </div>`;
  },

  _emoji(name) {
    const n = name.toLowerCase();
    if (n.includes('oud'))     return '🪵';
    if (n.includes('rose'))    return '🌹';
    if (n.includes('musk'))    return '🌿';
    if (n.includes('jasmine')) return '🌸';
    if (n.includes('amber'))   return '🌙';
    if (n.includes('citrus'))  return '🍋';
    return '🪷';
  },

  // ── Categories ────────────────────────────────────────
  updateCategories(cats) {
    if (!cats) return;
    const wrap = document.getElementById('rtCategoryChips');
    if (!wrap) return;
    const current = new URLSearchParams(window.location.search).get('category') || '';
    const isAdmin = document.body.dataset.admin === '1';
    const editBtn = isAdmin ? `<button class="chip" onclick="adminEditCategories()" style="border-style:dashed;border-color:var(--gold);color:var(--gold)">✏️ Edit</button>` : '';
    wrap.innerHTML = `
      <a href="/products" class="chip${!current ? ' active' : ''}">🌟 All Attars</a>
      ${cats.map(c => `<a href="/products?category=${c.id}" class="chip${current == c.id ? ' active' : ''}">${c.icon} ${c.name}</a>`).join('')}
      ${editBtn}`;
  },

  // ── Orders status live update ─────────────────────────
  async pollOrders() {
    try {
      const res  = await fetch('/api/order_status');
      const data = await res.json();
      data.orders.forEach(o => {
        const el = document.querySelector(`[data-order-status="${o.id}"]`);
        if (el && el.textContent.trim() !== o.status) {
          el.textContent    = o.status.charAt(0).toUpperCase() + o.status.slice(1);
          el.className      = `order-status status-${o.status}`;
          this._flash(el);
        }
      });
    } catch(e) {}
  },

  // ── Utility ───────────────────────────────────────────
  _flash(el) {
    el.classList.add('rt-flash');
    setTimeout(() => el.classList.remove('rt-flash'), 700);
  }
};

// CSS for flash animation
const rtStyle = document.createElement('style');
rtStyle.textContent = `
  .rt-flash {
    animation: rtFlashAnim 0.6s ease !important;
  }
  @keyframes rtFlashAnim {
    0%   { background: rgba(196,150,42,0.3); }
    100% { background: transparent; }
  }
`;
document.head.appendChild(rtStyle);

// Auto-start when DOM ready
document.addEventListener('DOMContentLoaded', () => RT.start());
