// =============================================
// Anas Aatar Wale — Image Cropper Utility
// Uses Cropper.js (loaded from CDN)
// =============================================

class AatarCropper {
  constructor(opts = {}) {
    this.aspectRatio = opts.aspectRatio ?? NaN; // NaN = free crop
    this.onSave      = opts.onSave || (() => {});
    this.outputSize  = opts.outputSize || 800;
    this._build();
  }

  _build() {
    if (document.getElementById('aatarCropperOverlay')) return;
    const overlay = document.createElement('div');
    overlay.id    = 'aatarCropperOverlay';
    overlay.innerHTML = `
      <div class="ac-backdrop"></div>
      <div class="ac-modal">
        <div class="ac-header">
          <span class="ac-title">✂️ Crop & Adjust Image</span>
          <button class="ac-close" id="acClose">✕</button>
        </div>
        <div class="ac-body">
          <div class="ac-canvas-wrap">
            <img id="acImg" src="" alt="crop">
          </div>
          <div class="ac-controls">
            <div class="ac-ctrl-row">
              <button class="ac-btn" id="acZoomIn"  title="Zoom In">🔍+</button>
              <button class="ac-btn" id="acZoomOut" title="Zoom Out">🔍−</button>
              <button class="ac-btn" id="acRotL"    title="Rotate Left">↺</button>
              <button class="ac-btn" id="acRotR"    title="Rotate Right">↻</button>
              <button class="ac-btn" id="acFlipH"   title="Flip Horizontal">↔</button>
              <button class="ac-btn" id="acFlipV"   title="Flip Vertical">↕</button>
              <button class="ac-btn" id="acReset"   title="Reset">⟳ Reset</button>
            </div>
            <div class="ac-ratio-row" id="acRatios">
              <span style="font-size:0.8rem;color:#666;margin-right:8px">Aspect:</span>
              <button class="ac-ratio-btn active" data-ratio="NaN">Free</button>
              <button class="ac-ratio-btn" data-ratio="1">1:1</button>
              <button class="ac-ratio-btn" data-ratio="1.777">16:9</button>
              <button class="ac-ratio-btn" data-ratio="0.75">3:4</button>
              <button class="ac-ratio-btn" data-ratio="1.5">3:2</button>
            </div>
          </div>
        </div>
        <div class="ac-footer">
          <button class="ac-btn-cancel" id="acCancel">Cancel</button>
          <button class="ac-btn-save"   id="acSave">✅ Set Image</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);

    // Styles
    const style = document.createElement('style');
    style.textContent = `
      #aatarCropperOverlay{position:fixed;inset:0;z-index:99999;display:none;align-items:center;justify-content:center}
      #aatarCropperOverlay.open{display:flex}
      .ac-backdrop{position:absolute;inset:0;background:rgba(0,0,0,0.75);backdrop-filter:blur(4px)}
      .ac-modal{position:relative;z-index:1;background:#fff;border-radius:18px;width:min(700px,95vw);max-height:90vh;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 30px 80px rgba(0,0,0,0.4);animation:acPopIn 0.3s cubic-bezier(.34,1.56,.64,1)}
      @keyframes acPopIn{from{transform:scale(0.85);opacity:0}to{transform:scale(1);opacity:1}}
      .ac-header{padding:16px 20px;border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
      .ac-title{font-weight:700;font-size:1rem;color:#3A1F0A}
      .ac-close{width:32px;height:32px;border-radius:8px;border:none;background:#f3f4f6;cursor:pointer;font-size:1rem;transition:all .2s}
      .ac-close:hover{background:#e5e7eb}
      .ac-body{flex:1;overflow:hidden;display:flex;flex-direction:column;padding:16px;gap:12px}
      .ac-canvas-wrap{flex:1;min-height:300px;max-height:420px;background:#1a1a1a;border-radius:12px;overflow:hidden;display:flex;align-items:center;justify-content:center}
      .ac-canvas-wrap img{max-width:100%;max-height:100%;display:block}
      .ac-controls{flex-shrink:0}
      .ac-ctrl-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}
      .ac-btn{padding:7px 14px;border-radius:8px;border:1.5px solid #e5e7eb;background:#f9fafb;cursor:pointer;font-size:0.82rem;font-weight:600;transition:all .2s;color:#374151}
      .ac-btn:hover{background:#5C3317;color:#fff;border-color:#5C3317}
      .ac-ratio-row{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
      .ac-ratio-btn{padding:5px 12px;border-radius:50px;border:1.5px solid #e5e7eb;background:#f9fafb;cursor:pointer;font-size:0.78rem;font-weight:600;transition:all .2s}
      .ac-ratio-btn.active,.ac-ratio-btn:hover{background:#C4962A;color:#fff;border-color:#C4962A}
      .ac-footer{padding:14px 20px;border-top:1px solid #eee;display:flex;gap:10px;justify-content:flex-end;flex-shrink:0}
      .ac-btn-cancel{padding:9px 22px;border-radius:10px;border:1.5px solid #e5e7eb;background:#f9fafb;cursor:pointer;font-weight:600;font-size:0.9rem;transition:all .2s}
      .ac-btn-cancel:hover{background:#e5e7eb}
      .ac-btn-save{padding:9px 28px;border-radius:10px;border:none;background:linear-gradient(135deg,#5C3317,#8B5E3C);color:#fff;cursor:pointer;font-weight:700;font-size:0.9rem;box-shadow:0 4px 14px rgba(92,51,23,.35);transition:all .2s}
      .ac-btn-save:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(92,51,23,.45)}
      /* Cropper.js override */
      .cropper-view-box,.cropper-face{border-radius:0}
    `;
    document.head.appendChild(style);

    // Load Cropper.js from CDN if not loaded
    if (!window.Cropper) {
      const link = document.createElement('link');
      link.rel  = 'stylesheet';
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.css';
      document.head.appendChild(link);
      const script  = document.createElement('script');
      script.src    = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.js';
      document.head.appendChild(script);
    }

    this._bindButtons();
  }

  _bindButtons() {
    const $ = id => document.getElementById(id);
    $('acClose').onclick  = () => this.close();
    $('acCancel').onclick = () => this.close();
    $('acSave').onclick   = () => this._save();
    $('acZoomIn').onclick  = () => this.cropper?.zoom(0.1);
    $('acZoomOut').onclick = () => this.cropper?.zoom(-0.1);
    $('acRotL').onclick    = () => this.cropper?.rotate(-90);
    $('acRotR').onclick    = () => this.cropper?.rotate(90);
    $('acFlipH').onclick   = () => { const d=this.cropper?.getData(); this.cropper?.scaleX(d?.scaleX===-1?1:-1); };
    $('acFlipV').onclick   = () => { const d=this.cropper?.getData(); this.cropper?.scaleY(d?.scaleY===-1?1:-1); };
    $('acReset').onclick   = () => this.cropper?.reset();

    document.querySelectorAll('.ac-ratio-btn').forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll('.ac-ratio-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const r = btn.dataset.ratio;
        this.cropper?.setAspectRatio(r === 'NaN' ? NaN : parseFloat(r));
      };
    });
  }

  open(file, aspectRatio) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
      const img = document.getElementById('acImg');
      img.src   = e.target.result;
      document.getElementById('aatarCropperOverlay').classList.add('open');
      // Wait for Cropper.js to load
      const init = () => {
        if (!window.Cropper) { setTimeout(init, 100); return; }
        if (this.cropper) { this.cropper.destroy(); this.cropper = null; }
        this.cropper = new Cropper(img, {
          aspectRatio: aspectRatio ?? this.aspectRatio,
          viewMode: 1,
          dragMode: 'move',
          autoCropArea: 0.9,
          responsive: true,
          restore: false,
          guides: true,
          center: true,
          highlight: false,
          cropBoxMovable: true,
          cropBoxResizable: true,
          toggleDragModeOnDblclick: false,
        });
      };
      setTimeout(init, 50);
    };
    reader.readAsDataURL(file);
  }

  _save() {
    if (!this.cropper) return;
    const canvas = this.cropper.getCroppedCanvas({
      maxWidth:  this.outputSize,
      maxHeight: this.outputSize,
      imageSmoothingEnabled: true,
      imageSmoothingQuality: 'high',
    });
    const dataURL = canvas.toDataURL('image/jpeg', 0.92);
    this.onSave(dataURL);
    this.close();
  }

  close() {
    document.getElementById('aatarCropperOverlay').classList.remove('open');
    if (this.cropper) { this.cropper.destroy(); this.cropper = null; }
  }
}

// ── Global helper: open file picker → cropper → callback ──
function openCropper(opts = {}) {
  // opts: { aspectRatio, onSave, outputSize, accept }
  const input  = document.createElement('input');
  input.type   = 'file';
  input.accept = opts.accept || 'image/*';
  input.onchange = e => {
    const file = e.target.files[0];
    if (!file) return;
    if (!window._aatarCropperInstance) {
      window._aatarCropperInstance = new AatarCropper({
        aspectRatio: opts.aspectRatio,
        outputSize:  opts.outputSize || 800,
        onSave: opts.onSave || (() => {}),
      });
    } else {
      window._aatarCropperInstance.aspectRatio = opts.aspectRatio;
      window._aatarCropperInstance.outputSize  = opts.outputSize || 800;
      window._aatarCropperInstance.onSave      = opts.onSave || (() => {});
    }
    window._aatarCropperInstance.open(file, opts.aspectRatio);
  };
  input.click();
}
