// =============================================
// Anas Aatar Wale - Main JS
// =============================================

// ─── PAGE LOADER ───
window.addEventListener('load', () => {
  const loader = document.getElementById('pageLoader');
  if (loader) {
    setTimeout(() => {
      loader.style.opacity = '0';
      setTimeout(() => loader.remove(), 400);
    }, 600);
  }
});

// ─── INTERSECTION OBSERVER FOR SCROLL ANIMATIONS ───
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.product-card, .section-header, .animate-on-scroll').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(30px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});

// ─── CART COUNT ───
function updateCartBadge() {
  fetch('/cart/count')
    .then(r => r.json())
    .then(data => {
      document.querySelectorAll('.cart-badge').forEach(b => {
        b.textContent = data.count;
        b.style.display = data.count > 0 ? 'flex' : 'none';
      });
    });
}
updateCartBadge();

// ─── ADD TO CART ───
function addToCart(productId, qty = 1) {
  const fd = new FormData();
  fd.append('product_id', productId);
  fd.append('qty', qty);
  return fetch('/cart/add', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        showToast('🛍️ Added to cart!', 'success');
        document.querySelectorAll('.cart-badge').forEach(b => {
          b.textContent = data.cart_count;
          b.style.display = 'flex';
          b.style.animation = 'none';
          requestAnimationFrame(() => b.style.animation = 'pulse 0.5s ease');
        });
      }
      return data;
    });
}

// ─── TOAST NOTIFICATION ───
function showToast(message, type = 'info', duration = 3000) {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ─── SUCCESS / ERROR POPUP MODAL ───
function showModal(type, title, message, onContinue) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  const isSuccess = type === 'success';
  overlay.innerHTML = `
    <div class="modal" style="position:relative">
      <div class="particles" id="modalParticles"></div>
      <div class="modal-icon ${type}">
        ${isSuccess ? '✅' : '❌'}
      </div>
      <h3 class="modal-title" style="color:${isSuccess ? '#2E7D52' : '#C0392B'}">${title}</h3>
      <p class="modal-msg" style="margin:10px 0 24px">${message}</p>
      <button class="btn btn-dark btn-block modal-continue-btn" style="border-radius:12px">
        ${isSuccess ? 'Continue 🎉' : 'Try Again'}
      </button>
    </div>`;
  document.body.appendChild(overlay);
  requestAnimationFrame(() => overlay.classList.add('active'));
  if (isSuccess) spawnParticles(overlay.querySelector('#modalParticles'));
  overlay.querySelector('.modal-continue-btn').onclick = () => {
    overlay.classList.remove('active');
    setTimeout(() => { overlay.remove(); if (onContinue) onContinue(); }, 300);
  };
}

function spawnParticles(container) {
  const colors = ['#C4962A', '#5C3317', '#E8B84B', '#8B5E3C', '#fff'];
  for (let i = 0; i < 12; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.cssText = `
      left:${Math.random()*100}%;
      top:${Math.random()*100}%;
      background:${colors[Math.floor(Math.random()*colors.length)]};
      animation-delay:${Math.random()*0.5}s;
    `;
    container.appendChild(p);
  }
}

// ─── WISHLIST TOGGLE ───
function toggleWishlist(productId, btn) {
  const fd = new FormData();
  fd.append('product_id', productId);
  fetch('/wishlist/toggle', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        btn.classList.toggle('active', data.wishlisted);
        btn.innerHTML = data.wishlisted ? '❤️' : '🤍';
        showToast(data.wishlisted ? '❤️ Added to wishlist!' : 'Removed from wishlist', data.wishlisted ? 'success' : 'info');
      }
    });
}

// ─── PRODUCT QUANTITY CONTROL ───
document.querySelectorAll('.qty-minus').forEach(btn => {
  btn.onclick = () => {
    const val = btn.parentElement.querySelector('.qty-value');
    if (parseInt(val.textContent) > 1) {
      val.textContent = parseInt(val.textContent) - 1;
      val.style.animation = 'scaleIn 0.2s ease';
    }
  };
});
document.querySelectorAll('.qty-plus').forEach(btn => {
  btn.onclick = () => {
    const val = btn.parentElement.querySelector('.qty-value');
    val.textContent = parseInt(val.textContent) + 1;
    val.style.animation = 'scaleIn 0.2s ease';
  };
});

// ─── SIZE SELECTION ───
document.querySelectorAll('.size-btn').forEach(btn => {
  btn.onclick = () => {
    btn.closest('.size-options').querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  };
});

// ─── SMOOTH NAVBAR ON SCROLL ───
window.addEventListener('scroll', () => {
  const nav = document.querySelector('.navbar');
  if (nav) {
    if (window.scrollY > 60) {
      nav.style.background = 'rgba(255,255,255,0.98)';
      nav.style.boxShadow = '0 4px 24px rgba(92,51,23,0.15)';
    } else {
      nav.style.background = 'rgba(255,255,255,0.95)';
    }
  }
});

// ─── CART SWIPE TO DELETE (on mobile) ───
document.querySelectorAll('.cart-item').forEach(item => {
  let startX = 0;
  item.addEventListener('touchstart', e => startX = e.touches[0].clientX, {passive:true});
  item.addEventListener('touchend', e => {
    const diff = startX - e.changedTouches[0].clientX;
    if (diff > 80) {
      item.style.transform = 'translateX(-100%)';
      item.style.opacity = '0';
      item.style.transition = 'all 0.3s';
    }
  }, {passive:true});
});

// ─── SEARCH AUTO-SUBMIT ON ENTER ───
const searchInput = document.getElementById('searchInput');
if (searchInput) {
  searchInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') {
      const params = new URLSearchParams(window.location.search);
      params.set('search', searchInput.value);
      window.location.search = params.toString();
    }
  });
}

// ─── CATEGORY FILTER (instant) ───
document.querySelectorAll('.chip[data-cat]').forEach(chip => {
  chip.onclick = (e) => {
    e.preventDefault();
    const cat = chip.dataset.cat;
    const params = new URLSearchParams(window.location.search);
    if (cat) params.set('category', cat); else params.delete('category');
    window.location.search = params.toString();
  };
});

// ─── LOGIN / REGISTER AJAX ───
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.onsubmit = e => {
    e.preventDefault();
    const btn = loginForm.querySelector('button[type=submit]');
    const original = btn.innerHTML;
    btn.innerHTML = '<span class="loader" style="width:20px;height:20px;border-width:2px;display:inline-block"></span>';
    btn.disabled = true;
    const fd = new FormData(loginForm);
    const next = new URLSearchParams(window.location.search).get('next') || '';
    fetch(`/login${next ? '?next='+next : ''}`, { method: 'POST', body: fd })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          showModal('success', 'Welcome Back! 🎉', 'Login successful. Redirecting...', () => window.location.href = data.redirect);
        } else {
          showModal('error', 'Login Failed', data.message);
          btn.innerHTML = original;
          btn.disabled = false;
        }
      });
  };
}

const registerForm = document.getElementById('registerForm');
if (registerForm) {
  registerForm.onsubmit = e => {
    e.preventDefault();
    const pwd = registerForm.querySelector('[name=password]').value;
    const cpwd = registerForm.querySelector('[name=confirm_password]').value;
    if (pwd !== cpwd) { showToast('Passwords do not match!', 'error'); return; }
    const fd = new FormData(registerForm);
    fetch('/register', { method: 'POST', body: fd })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          showModal('success', 'Account Created! 🎉', 'Your account is ready. Please login.', () => window.location.href = '/login');
        } else {
          showModal('error', 'Registration Failed', data.message);
        }
      });
  };
}

// ─── CHECKOUT FORM FLOW ───
const checkoutForm = document.getElementById('checkoutShippingForm');
if (checkoutForm) {
  checkoutForm.onsubmit = e => {
    e.preventDefault();
    const fd = new FormData(checkoutForm);
    fd.append('step', 'shipping');
    fetch('/checkout', { method: 'POST', body: fd })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          document.getElementById('shippingStep').classList.remove('active');
          document.getElementById('paymentStep').classList.add('active');
          document.querySelector('.step[data-step="1"]').classList.add('done');
          document.querySelector('.step[data-step="2"]').classList.add('active');
          window.scrollTo({top:0, behavior:'smooth'});
        }
      });
  };
}

// Payment form now handled in checkout.html template (includes Razorpay)

// ─── UPDATE CART QTY ───
function updateCartQty(productId, qty) {
  const fd = new FormData();
  fd.append('product_id', productId);
  fd.append('qty', qty);
  fetch('/cart/update', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(() => location.reload());
}

function removeFromCart(productId) {
  const fd = new FormData();
  fd.append('product_id', productId);
  fetch('/cart/remove', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(() => {
      showToast('Removed from cart', 'info');
      setTimeout(() => location.reload(), 800);
    });
}

// ─── STAGGERED CARD ANIMATION ───
document.querySelectorAll('.product-card').forEach((card, i) => {
  card.style.animationDelay = `${i * 0.08}s`;
});
