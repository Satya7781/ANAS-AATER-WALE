// =============================================
// Anas Aatar Wale — Admin Inline Edit Tools
// =============================================

// ── Three-dot menu toggle ─────────────────────
function toggleDotMenu(btn) {
  const dropdown = btn.nextElementSibling;
  // Close all others first
  document.querySelectorAll('.dot-menu-dropdown.open').forEach(d => {
    if (d !== dropdown) d.classList.remove('open');
  });
  dropdown.classList.toggle('open');
  // Close on outside click
  setTimeout(() => {
    document.addEventListener('click', function handler() {
      dropdown.classList.remove('open');
      document.removeEventListener('click', handler);
    });
  }, 10);
}

// ── Load categories into select dropdowns ─────
function loadCategories() {
  fetch('/api/realtime')
    .then(r => r.json())
    .then(data => {
      ['inlineEditCategory', 'inlineAddCategory'].forEach(id => {
        const sel = document.getElementById(id);
        if (!sel) return;
        sel.innerHTML = data.categories.map(c =>
          `<option value="${c.id}">${c.icon} ${c.name}</option>`
        ).join('');
      });
      // Also populate cat editor
      const list = document.getElementById('catEditorList');
      if (list) renderCatList(data.categories);
    })
    .catch(e => console.error('loadCategories error:', e));
}

// ── Admin: Edit product (opens modal with data) ─
function adminEditProduct(pid) {
  fetch('/api/realtime')
    .then(r => r.json())
    .then(data => {
      const p = data.products.find(x => x.id == pid);
      if (!p) { showAdminToast('Product not found!', 'error'); return; }

      const get = id => document.getElementById(id);
      get('inlineEditId').value    = p.id;
      get('inlineEditName').value  = p.name || '';
      get('inlineEditPrice').value = p.price || '';
      get('inlineEditStock').value = p.stock || '';
      get('inlineEditVolume').value= p.volume || '';
      get('inlineEditDesc').value  = p.description || '';
      get('inlineEditRating').value= p.rating || 4.5;
      get('inlineEditImgData').value = '';

      const prev = get('inlineEditImgPreview');
      if (p.image) { prev.src = p.image; prev.style.display = 'block'; }
      else         { prev.src = '';      prev.style.display = 'none';  }

      const sel = get('inlineEditCategory');
      if (sel) sel.value = p.category_id || '';

      get('inlineEditModal').classList.add('active');
    })
    .catch(e => { console.error(e); showAdminToast('Error loading product!', 'error'); });
}

// ── Admin: Change only product image ──────────
function adminEditProductImage(pid) {
  openCropper({
    aspectRatio: 1,
    outputSize: 600,
    onSave: (dataURL) => {
      // Show immediately on all matching cards
      document.querySelectorAll(`[data-rt-img="${pid}"]`).forEach(el => el.src = dataURL);
      // Save to server
      fetch(`/admin/products/edit/${pid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ _imageOnly: true, image_data: dataURL })
      })
      .then(r => r.json())
      .then(d => {
        if (d.success) showAdminToast('🖼️ Image updated!');
        else showAdminToast('Error: ' + (d.error || 'Failed'), 'error');
      })
      .catch(e => showAdminToast('Network error!', 'error'));
    }
  });
}

// ── Admin: Delete product ─────────────────────
function adminDeleteProduct(pid, name) {
  if (!confirm(`Delete "${name}"?\n\nThis cannot be undone.`)) return;
  fetch(`/admin/products/delete/${pid}`, { method: 'POST' })
    .then(r => r.json())
    .then(d => {
      if (d.success) {
        showAdminToast('🗑️ Product deleted!', 'error');
        // Remove card from DOM immediately
        document.querySelectorAll(`[data-rt-img="${pid}"]`).forEach(el => {
          const card = el.closest('.product-card');
          if (card) card.style.animation = 'fadeOut 0.3s ease forwards';
          setTimeout(() => card && card.remove(), 300);
        });
      }
    })
    .catch(e => showAdminToast('Network error!', 'error'));
}

// ── Admin: Add product card click ─────────────
function adminOpenAddProduct() {
  ['inlineAddName','inlineAddPrice','inlineAddStock','inlineAddVolume','inlineAddDesc'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const r = document.getElementById('inlineAddRating');
  if (r) r.value = '4.5';
  const prev = document.getElementById('inlineAddImgPreview');
  if (prev) { prev.src = ''; prev.style.display = 'none'; }
  const imgData = document.getElementById('inlineAddImgData');
  if (imgData) imgData.value = '';
  document.getElementById('inlineAddModal').classList.add('active');
}

// ── Modal open/close ──────────────────────────
function openInlineEditModal()  { document.getElementById('inlineEditModal').classList.add('active'); }
function closeInlineEditModal() { document.getElementById('inlineEditModal').classList.remove('active'); }
function openInlineAddModal()   { document.getElementById('inlineAddModal').classList.add('active'); }
function closeInlineAddModal()  { document.getElementById('inlineAddModal').classList.remove('active'); }

// ── Submit: Edit product ──────────────────────
function submitInlineEdit() {
  const get  = id => document.getElementById(id);
  const pid  = get('inlineEditId').value;
  const name = get('inlineEditName').value.trim();
  const price= get('inlineEditPrice').value;

  if (!name || !price) {
    showAdminToast('Name and price are required!', 'error');
    return;
  }

  const btn = document.querySelector('#inlineEditModal .btn-save-modal');
  if (btn) { btn.disabled = true; btn.textContent = 'Saving...'; }

  const data = {
    name,
    price,
    description: get('inlineEditDesc').value  || '',
    stock:       get('inlineEditStock').value || 0,
    volume:      get('inlineEditVolume').value|| '',
    rating:      get('inlineEditRating').value|| 4.5,
    category_id: get('inlineEditCategory')?.value || 1,
    is_active:   1,
    image_data:  get('inlineEditImgData').value || null,
  };

  fetch(`/admin/products/edit/${pid}`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(data)
  })
  .then(r => r.json())
  .then(d => {
    if (btn) { btn.disabled = false; btn.textContent = '💾 Save'; }
    if (d.success) {
      showAdminToast('✅ Product updated!');
      closeInlineEditModal();
    } else {
      showAdminToast('Error: ' + (d.error || 'Failed'), 'error');
    }
  })
  .catch(e => {
    if (btn) { btn.disabled = false; btn.textContent = '💾 Save'; }
    showAdminToast('Network error!', 'error');
  });
}

// ── Submit: Add product ───────────────────────
function submitInlineAdd() {
  const get  = id => document.getElementById(id);
  const name = get('inlineAddName').value.trim();
  const price= get('inlineAddPrice').value;

  if (!name || !price) {
    showAdminToast('Name and price are required!', 'error');
    return;
  }

  const btn = document.querySelector('#inlineAddModal .btn-save-modal');
  if (btn) { btn.disabled = true; btn.textContent = 'Adding...'; }

  const data = {
    name,
    price,
    description: get('inlineAddDesc').value  || '',
    stock:       get('inlineAddStock').value || 0,
    volume:      get('inlineAddVolume').value|| '',
    rating:      get('inlineAddRating')?.value || 4.5,
    category_id: get('inlineAddCategory')?.value || 1,
    image_data:  get('inlineAddImgData').value || null,
  };

  fetch('/admin/products/add', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(data)
  })
  .then(r => r.json())
  .then(d => {
    if (btn) { btn.disabled = false; btn.textContent = '➕ Add Product'; }
    if (d.success) {
      showAdminToast('✅ Product added! Page will refresh shortly.');
      closeInlineAddModal();
    } else {
      showAdminToast('Error: ' + (d.error || 'Failed'), 'error');
    }
  })
  .catch(e => {
    if (btn) { btn.disabled = false; btn.textContent = '➕ Add Product'; }
    showAdminToast('Network error!', 'error');
  });
}

// ── Hero editor open/close ────────────────────
function openHeroEditor()  { document.getElementById('heroEditorOverlay').classList.add('active'); }
function closeHeroEditor() { document.getElementById('heroEditorOverlay').classList.remove('active'); }

// ── Save hero/logo/settings ───────────────────
function saveHeroSettingsAll() {
  const get = id => document.getElementById(id);
  const logoData = get('logoImgData2')?.value || get('logoImgData')?.value || null;

  const data = {
    hero_title:      get('heroTitleInput').value,
    hero_subtitle:   get('heroSubtitleInput').value,
    site_name:       get('siteNameInput').value,
    hero_image_data: get('heroImgData')?.value || null,
    logo_image_data: logoData,
  };

  const btn = get('heroSaveBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Saving...'; }

  fetch('/admin/settings/save', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(data)
  })
  .then(r => r.json())
  .then(d => {
    if (btn) { btn.disabled = false; btn.textContent = '💾 Save Changes'; }
    if (d.success) {
      showAdminToast('✅ Settings saved! Updating live...');
      closeHeroEditor();
    } else {
      showAdminToast('Error saving settings!', 'error');
    }
  })
  .catch(e => {
    if (btn) { btn.disabled = false; btn.textContent = '💾 Save Changes'; }
    showAdminToast('Network error!', 'error');
  });
}

// ── Category editor ───────────────────────────
function adminEditCategories() {
  loadCategories(); // refresh list
  document.getElementById('catEditorOverlay').classList.add('active');
}
function closeCatEditor() {
  document.getElementById('catEditorOverlay').classList.remove('active');
}

function renderCatList(cats) {
  const list = document.getElementById('catEditorList');
  if (!list) return;
  list.innerHTML = cats.map(c => `
    <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px">
      <input value="${c.icon}" id="catIcon${c.id}"
             style="width:52px;border:1.5px solid #e5e7eb;border-radius:8px;padding:8px;text-align:center;font-size:1.2rem">
      <input value="${c.name}" id="catName${c.id}"
             style="flex:1;border:1.5px solid #e5e7eb;border-radius:8px;padding:8px 12px;font-family:Poppins,sans-serif;font-size:0.9rem">
      <button onclick="saveCategory(${c.id}, document.getElementById('catName${c.id}').value, document.getElementById('catIcon${c.id}').value)"
              style="padding:8px 14px;border-radius:8px;border:none;background:#5C3317;color:white;cursor:pointer;font-weight:600;font-size:0.82rem;white-space:nowrap">
        Save
      </button>
    </div>`).join('');
}

function addCatRow() {
  const list = document.getElementById('catEditorList');
  const div  = document.createElement('div');
  div.style.cssText = 'display:flex;gap:8px;align-items:center;margin-bottom:10px';
  div.innerHTML = `
    <input placeholder="🏷️" id="newCatIcon"
           style="width:52px;border:1.5px solid #C4962A;border-radius:8px;padding:8px;text-align:center;font-size:1.2rem">
    <input placeholder="Category name..." id="newCatName"
           style="flex:1;border:1.5px solid #C4962A;border-radius:8px;padding:8px 12px;font-family:Poppins,sans-serif;font-size:0.9rem">
    <button onclick="saveCategory(null, document.getElementById('newCatName').value, document.getElementById('newCatIcon').value||'🏷️')"
            style="padding:8px 14px;border-radius:8px;border:none;background:#C4962A;color:white;cursor:pointer;font-weight:600;font-size:0.82rem;white-space:nowrap">
      Add
    </button>`;
  list.appendChild(div);
  div.querySelector('input').focus();
}

function saveCategory(id, name, icon) {
  if (!name.trim()) { showAdminToast('Category name required!', 'error'); return; }
  fetch('/admin/categories/save', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ id, name: name.trim(), icon: icon || '🏷️' })
  })
  .then(r => r.json())
  .then(d => {
    if (d.success) showAdminToast('✅ Category saved!');
    else showAdminToast('Error!', 'error');
  })
  .catch(() => showAdminToast('Network error!', 'error'));
}

// ── Toast notification ────────────────────────
function showAdminToast(msg, type = 'success') {
  let container = document.getElementById('adminToastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'adminToastContainer';
    container.style.cssText = 'position:fixed;bottom:80px;right:20px;z-index:99999;display:flex;flex-direction:column;gap:8px;pointer-events:none';
    document.body.appendChild(container);
  }
  const colors = { success: '#5C3317', error: '#DC2626', info: '#1F2937' };
  const toast = document.createElement('div');
  toast.style.cssText = `
    background:${colors[type]||colors.success};color:white;
    padding:12px 20px;border-radius:12px;font-size:0.88rem;font-weight:600;
    box-shadow:0 8px 24px rgba(0,0,0,0.25);pointer-events:auto;
    animation:slideInRight 0.35s cubic-bezier(0.34,1.56,0.64,1);
    max-width:280px;
  `;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s,transform 0.3s';
    toast.style.opacity    = '0';
    toast.style.transform  = 'translateX(20px)';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Inject toast animation CSS
const toastStyle = document.createElement('style');
toastStyle.textContent = `
  @keyframes slideInRight { from{opacity:0;transform:translateX(30px)} to{opacity:1;transform:translateX(0)} }
  @keyframes fadeOut      { to{opacity:0;transform:scale(0.9)} }
`;
document.head.appendChild(toastStyle);

// Auto-load categories when admin page loads
document.addEventListener('DOMContentLoaded', loadCategories);
