from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import pymysql
import hashlib, os, base64, time, json
from datetime import datetime
from functools import wraps
import razorpay

app = Flask(__name__)
app.secret_key = 'anas_aatar_wale_secret_2024'

# ── MySQL ─────────────────────────────────────────────────
app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'anas_user'
app.config['MYSQL_PASSWORD'] = 'StrongPassw0rd!'
app.config['MYSQL_DB']       = 'anas_aatar_db'

# ── Razorpay ──────────────────────────────────────────────
# 🔑 UPDATE THESE with your Razorpay live/test credentials
app.config['RAZORPAY_KEY_ID']     = 'rzp_test_xxxxxxxxxxxx'
app.config['RAZORPAY_KEY_SECRET'] = 'your_razorpay_secret'
razorpay_client = razorpay.Client(auth=(
    app.config['RAZORPAY_KEY_ID'],
    app.config['RAZORPAY_KEY_SECRET']
))

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ─────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────
def hash_password(p):
    # FIX #5 (DB): use SHA256 — stored as hex, NOT plaintext
    return hashlib.sha256(p.encode()).hexdigest()

def save_base64_image(data_url, filename):
    """Save a base64 cropped image to disk, return relative URL."""
    if not data_url or not data_url.startswith('data:image'):
        return None
    try:
        header, encoded = data_url.split(',', 1)
        ext = header.split('/')[1].split(';')[0]
        if ext not in ['jpeg','jpg','png','webp','gif']:
            ext = 'jpg'
        fname = f"{filename}_{int(time.time())}.{ext}"
        path  = os.path.join(UPLOAD_FOLDER, fname)
        with open(path, 'wb') as f:
            f.write(base64.b64decode(encoded))
        return f"/static/uploads/{fname}"
    except Exception as e:
        print(f"Image save error: {e}")
        return None


def format_timestamp(value, fmt):
    if hasattr(value, 'strftime'):
        return value.strftime(fmt)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).strftime(fmt)
        except ValueError:
            return value
    return value

def get_site_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM site_settings LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        row = {
            'hero_title':    'Discover Your <span>Signature</span> Fragrance',
            'hero_subtitle': 'Handcrafted attars and perfumes made with the finest natural ingredients.',
            'hero_image':    '',
            'logo_image':    '',
            'site_name':     'Anas Aatar Wale',
            'fast_delivery_title': 'Fast Delivery',
            'fast_delivery_text': '3-5 business days',
            'secure_payment_title': 'Secure Payment',
            'secure_payment_text': '100% safe checkout',
            'easy_returns_title': 'Easy Returns',
            'easy_returns_text': '7 day return policy',
            'authentic_title': 'Authentic',
            'authentic_text': '100% genuine product',
            'updated_at': datetime.now()
        }
    return row


# Database connection function
def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

def migrate_razorpay_columns():
    """Add Razorpay columns to orders table if they don't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM orders LIKE 'razorpay_order_id'")
        if not cursor.fetchone():
            cursor.execute("""ALTER TABLE orders
                ADD COLUMN razorpay_order_id VARCHAR(100) NULL AFTER total,
                ADD COLUMN razorpay_payment_id VARCHAR(100) NULL AFTER razorpay_order_id,
                ADD COLUMN razorpay_signature VARCHAR(255) NULL AFTER razorpay_payment_id""")
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Migration note: {e}")

# Run migration on startup
migrate_razorpay_columns()

def login_required(f):
    @wraps(f)
    def deco(*a, **kw):
        if 'user_id' not in session:
            return redirect(url_for('login') + '?next=' + request.path)
        return f(*a, **kw)
    return deco

def admin_required(f):
    @wraps(f)
    def deco(*a, **kw):
        if 'admin_id' not in session:
            return redirect(url_for('login') + '?admin=1')
        return f(*a, **kw)
    return deco

# ─────────────────────────────────────────────────────────
#  REAL-TIME API  (polled every 3 s by all pages)
# ─────────────────────────────────────────────────────────
@app.route('/api/realtime')
def api_realtime():
    conn = get_db_connection()
    cursor = conn.cursor()

    # products
    cursor.execute("""SELECT p.id, p.name, p.price, p.stock, p.rating,
                             p.volume, p.image, p.is_active,
                             c.name as category_name
                      FROM products p
                      LEFT JOIN categories c ON p.category_id = c.id
                      WHERE p.is_active = 1
                      ORDER BY p.created_at DESC""")
    products = cursor.fetchall()
    for p in products:
        p['price'] = float(p['price'])
        p['rating'] = float(p['rating']) if p['rating'] else 4.0

    # categories
    cursor.execute("SELECT id, name, icon FROM categories ORDER BY id")
    cats = cursor.fetchall()

    # site settings
    settings = get_site_settings()
    settings.pop('updated_at', None)

    # featured (top 8) + top_rated (top 4)
    featured   = [p for p in products[:8]]
    top_rated  = sorted(products, key=lambda x: x['rating'], reverse=True)[:4]

    conn.close()
    return jsonify({
        'products':   products,
        'featured':   featured,
        'top_rated':  top_rated,
        'categories': cats,
        'settings':   settings,
        'ts':         int(time.time())
    })

@app.route('/api/product/<int:pid>')
def api_product(pid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT p.*, c.name as category_name
                      FROM products p LEFT JOIN categories c ON p.category_id = c.id
                      WHERE p.id = %s""", (pid,))
    p = cursor.fetchone()
    if p:
        p['price'] = float(p['price'])
        p['rating'] = float(p['rating']) if p['rating'] else 4.0
    cursor.execute("""SELECT p.id,p.name,p.price,p.image,p.volume
                      FROM products p WHERE category_id=%s AND id!=%s AND is_active=1 LIMIT 4""",
                   (p['category_id'] if p else 0, pid))
    related = cursor.fetchall()
    for r in related: r['price'] = float(r['price'])
    conn.close()
    return jsonify({'product': p, 'related': related})

@app.route('/api/order_status')
@login_required
def api_order_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, status, total FROM orders WHERE user_id=%s ORDER BY created_at DESC",
                   (session['user_id'],))
    orders = cursor.fetchall()
    for o in orders: o['total'] = float(o['total'])
    conn.close()
    return jsonify({'orders': orders})

# FIX: User notifications API
@app.route('/api/notifications')
@login_required
def api_notifications():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT id, title, message, is_read, created_at
                      FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 20""",
                   (session['user_id'],))
    notifs = cursor.fetchall()
    for n in notifs:
        if n.get('created_at'):
            n['created_at'] = format_timestamp(n['created_at'], '%d %b %Y, %I:%M %p')
    cursor.execute("SELECT COUNT(*) as c FROM notifications WHERE user_id=%s AND is_read=0",
                   (session['user_id'],))
    unread = cursor.fetchone()['c']
    conn.close()
    return jsonify({'notifications': notifs, 'unread': unread})

@app.route('/api/notifications/mark_read', methods=['POST'])
@login_required
def mark_notifications_read():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s", (session['user_id'],))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# FIX: Admin notifications API
@app.route('/api/admin/notifications')
@admin_required
def api_admin_notifications():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT o.id, o.total, o.status, o.created_at,
                             u.first_name, u.last_name
                      FROM orders o JOIN users u ON o.user_id=u.id
                      WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                      ORDER BY o.created_at DESC LIMIT 10""")
    recent_orders = cursor.fetchall()
    for o in recent_orders:
        o['total'] = float(o['total'])
        if o.get('created_at'):
            o['created_at'] = format_timestamp(o['created_at'], '%d %b %Y, %I:%M %p')
    cursor.execute("SELECT COUNT(*) as c FROM orders WHERE status='pending'")
    pending_count = cursor.fetchone()['c']
    conn.close()
    return jsonify({'recent_orders': recent_orders, 'pending_count': pending_count})

# FIX: Product reviews API
@app.route('/api/product/<int:pid>/reviews')
def api_product_reviews(pid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT r.*, u.first_name, u.last_name
                      FROM product_reviews r JOIN users u ON r.user_id=u.id
                      WHERE r.product_id=%s ORDER BY r.created_at DESC""", (pid,))
    reviews = cursor.fetchall()
    for r in reviews:
        if r.get('created_at'):
            r['created_at'] = format_timestamp(r['created_at'], '%d %b %Y')
    cursor.execute("SELECT AVG(rating) as avg, COUNT(*) as cnt FROM product_reviews WHERE product_id=%s", (pid,))
    stats = cursor.fetchone()
    conn.close()
    return jsonify({
        'reviews': reviews,
        'avg_rating': float(stats['avg']) if stats['avg'] else 0,
        'total': stats['cnt']
    })

@app.route('/api/product/<int:pid>/review', methods=['POST'])
@login_required
def submit_review(pid):
    data = request.get_json(force=True) or {}
    rating = int(data.get('rating', 5))
    comment = data.get('comment', '').strip()
    if not comment:
        return jsonify({'success': False, 'error': 'Comment required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if user already reviewed
    cursor.execute("SELECT id FROM product_reviews WHERE user_id=%s AND product_id=%s",
                   (session['user_id'], pid))
    if cursor.fetchone():
        return jsonify({'success': False, 'error': 'You already reviewed this product'}), 400
    cursor.execute("""INSERT INTO product_reviews(user_id, product_id, rating, comment, created_at)
                      VALUES(%s,%s,%s,%s,NOW())""",
                   (session['user_id'], pid, rating, comment))
    # Update product average rating
    cursor.execute("SELECT AVG(rating) as avg FROM product_reviews WHERE product_id=%s", (pid,))
    avg = cursor.fetchone()['avg']
    if avg:
        cursor.execute("UPDATE products SET rating=%s WHERE id=%s", (round(float(avg), 1), pid))
    # Add notification for user
    cursor.execute("""INSERT INTO notifications(user_id, title, message, created_at)
                      VALUES(%s, 'Review Submitted', %s, NOW())""",
                   (session['user_id'], f'Your review for product #{pid} was submitted.'))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ─────────────────────────────────────────────────────────
#  RAZORPAY PAYMENT ROUTES
# ─────────────────────────────────────────────────────────
@app.route('/api/create-razorpay-order', methods=['POST'])
@login_required
def create_razorpay_order():
    """Create a Razorpay order and return order_id + amount."""
    cart = session.get('cart', {})
    if not cart:
        return jsonify({'success': False, 'error': 'Cart is empty'}), 400
    total = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    for pid, qty in cart.items():
        cursor.execute("SELECT price FROM products WHERE id=%s", (pid,))
        p = cursor.fetchone()
        if p:
            total += float(p['price']) * qty
    conn.close()
    ship_c = 50.0
    tax    = round(total * 0.08, 2)
    grand  = int(round((total + ship_c + tax) * 100))  # Razorpay expects paise
    try:
        razorpay_order = razorpay_client.order.create({
            'amount': grand,
            'currency': 'INR',
            'receipt': f'receipt_{int(time.time())}',
            'payment_capture': 1
        })
        return jsonify({
            'success': True,
            'razorpay_order_id': razorpay_order['id'],
            'amount': grand,
            'currency': 'INR',
            'key_id': app.config['RAZORPAY_KEY_ID'],
            'subtotal': total,
            'shipping': ship_c,
            'tax': tax,
            'total': (total + ship_c + tax)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/verify-razorpay-payment', methods=['POST'])
@login_required
def verify_razorpay_payment():
    """Verify Razorpay payment signature, then create the order."""
    data = request.get_json(force=True) or {}
    razorpay_order_id   = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature  = data.get('razorpay_signature')
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return jsonify({'success': False, 'error': 'Missing payment details'}), 400
    # Verify signature
    params_dict = {
        'razorpay_order_id':   razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature':  razorpay_signature
    }
    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
    except Exception:
        return jsonify({'success': False, 'error': 'Payment verification failed'}), 400
    # Signature valid — create the order in DB
    cart = session.get('cart', {})
    if not cart:
        return jsonify({'success': False, 'error': 'Cart is empty'}), 400
    cart_items = []; total = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    for pid, qty in cart.items():
        cursor.execute("SELECT * FROM products WHERE id=%s", (pid,))
        p = cursor.fetchone()
        if p:
            p['qty'] = qty; p['subtotal'] = float(p['price']) * qty
            total += p['subtotal']; cart_items.append(p)
    sh      = session.get('shipping', {})
    ship_c  = 50.0
    tax     = round(total * 0.08, 2)
    grand   = total + ship_c + tax
    cursor.execute("""INSERT INTO orders
        (user_id,first_name,last_name,address,city,zip_code,state,country,
         phone,subtotal,shipping_cost,tax,total,payment_method,status,created_at,
         razorpay_order_id,razorpay_payment_id,razorpay_signature)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'razorpay','pending',NOW(),
               %s,%s,%s)""",
        (session['user_id'], sh.get('first_name',''), sh.get('last_name',''),
         sh.get('address',''), sh.get('city',''), sh.get('zip',''),
         sh.get('state',''), sh.get('country',''), sh.get('phone',''),
         total, ship_c, tax, grand,
         razorpay_order_id, razorpay_payment_id, razorpay_signature))
    oid = cursor.lastrowid
    for item in cart_items:
        cursor.execute("""INSERT INTO order_items(order_id,product_id,qty,price)
                          VALUES(%s,%s,%s,%s)""",
                       (oid, item['id'], item['qty'], item['price']))
    cursor.execute("""INSERT INTO notifications(user_id, title, message, created_at)
                      VALUES(%s, 'Order Placed! 🎉', %s, NOW())""",
                   (session['user_id'], f'Your order #{oid} has been placed successfully. Payment: Razorpay. Total: ₹{grand:.0f}'))
    conn.commit()
    session.pop('cart', None); session.pop('shipping', None)
    conn.close()
    return jsonify({'success': True, 'order_id': oid})

# ─────────────────────────────────────────────────────────
#  SINGLE LOGIN / REGISTER
# ─────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    # FIX #5 (User): Remove back button - redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('index'))
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '')
        password   = hash_password(request.form.get('password', ''))
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check admin first
        cursor.execute("SELECT * FROM admins WHERE username=%s AND password=%s",
                       (identifier, password))
        admin = cursor.fetchone()
        if admin:
            session['admin_id']   = admin['id']
            session['admin_name'] = admin['username']
            conn.close()
            return jsonify({'success': True, 'role': 'admin',
                            'redirect': url_for('admin_dashboard')})

        # Check user (email)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s",
                       (identifier, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id']    = user['id']
            session['user_name']  = user['first_name']
            session['user_email'] = user['email']
            next_page = request.args.get('next', url_for('index'))
            return jsonify({'success': True, 'role': 'user', 'redirect': next_page})

        return jsonify({'success': False, 'message': 'Invalid credentials. Please try again.'})

    is_admin = request.args.get('admin', '0') == '1'
    return render_template('user/login.html', is_admin=is_admin)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name  = request.form.get('last_name', '')
        email      = request.form['email']
        password   = hash_password(request.form['password'])
        phone      = request.form.get('phone', '')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Email already registered.'})
        cursor.execute("""INSERT INTO users (first_name,last_name,email,password,phone)
                          VALUES (%s,%s,%s,%s,%s)""",
                       (first_name, last_name, email, password, phone))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    return render_template('user/register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─────────────────────────────────────────────────────────
#  USER ROUTES
# ─────────────────────────────────────────────────────────
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.execute("""SELECT p.*, c.name as category_name FROM products p
                      LEFT JOIN categories c ON p.category_id=c.id
                      WHERE p.is_active=1 ORDER BY p.created_at DESC LIMIT 8""")
    featured = cursor.fetchall()
    cursor.execute("""SELECT p.*, c.name as category_name FROM products p
                      LEFT JOIN categories c ON p.category_id=c.id
                      WHERE p.is_active=1 ORDER BY p.rating DESC LIMIT 4""")
    top_rated = cursor.fetchall()
    settings = get_site_settings()
    conn.close()
    return render_template('user/index.html', categories=categories,
                           featured=featured, top_rated=top_rated, settings=settings)

@app.route('/products')
def products():
    category_id = request.args.get('category', '')
    search      = request.args.get('search', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    q = """SELECT p.*, c.name as category_name FROM products p
           LEFT JOIN categories c ON p.category_id=c.id WHERE p.is_active=1"""
    params = []
    if category_id:
        q += " AND p.category_id=%s"; params.append(category_id)
    if search:
        q += " AND (p.name LIKE %s OR p.description LIKE %s)"
        params += [f'%{search}%', f'%{search}%']
    cursor.execute(q, params)
    prods = cursor.fetchall()
    conn.close()
    return render_template('user/products.html', products=prods,
                           categories=categories,
                           selected_category=category_id,
                           search=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT p.*, c.name as category_name FROM products p
                      LEFT JOIN categories c ON p.category_id=c.id WHERE p.id=%s""",
                   (product_id,))
    product = cursor.fetchone()
    if not product:
        return redirect(url_for('index'))
    cursor.execute("""SELECT * FROM products WHERE category_id=%s AND id!=%s AND is_active=1 LIMIT 4""",
                   (product['category_id'], product_id))
    related = cursor.fetchall()
    # FIX #4: Load reviews
    cursor.execute("""SELECT r.*, u.first_name, u.last_name
                      FROM product_reviews r JOIN users u ON r.user_id=u.id
                      WHERE r.product_id=%s ORDER BY r.created_at DESC""", (product_id,))
    reviews = cursor.fetchall()
    for r in reviews:
        if r.get('created_at'):
            r['created_at'] = format_timestamp(r['created_at'], '%d %b %Y')
    # Check if user already reviewed
    user_reviewed = False
    if 'user_id' in session:
        cursor.execute("SELECT id FROM product_reviews WHERE user_id=%s AND product_id=%s",
                       (session['user_id'], product_id))
        user_reviewed = cursor.fetchone() is not None
    conn.close()
    return render_template('user/product_detail.html', product=product,
                           related=related, reviews=reviews, user_reviewed=user_reviewed)

@app.route('/cart')
def cart():
    cart       = session.get('cart', {})
    cart_items = []
    total      = 0
    if cart:
        conn = get_db_connection()
        cursor = conn.cursor()
        for pid, qty in cart.items():
            cursor.execute("SELECT * FROM products WHERE id=%s", (pid,))
            p = cursor.fetchone()
            if p:
                p['qty']      = qty
                p['subtotal'] = float(p['price']) * qty
                total        += p['subtotal']
                cart_items.append(p)
        conn.close()
    return render_template('user/cart.html', cart_items=cart_items, total=total)

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    pid  = str(request.form.get('product_id'))
    qty  = int(request.form.get('qty', 1))
    cart = session.get('cart', {})
    cart[pid] = cart.get(pid, 0) + qty
    session['cart'] = cart
    return jsonify({'success': True, 'cart_count': sum(cart.values())})

@app.route('/cart/update', methods=['POST'])
def update_cart():
    pid  = str(request.form.get('product_id'))
    qty  = int(request.form.get('qty', 1))
    cart = session.get('cart', {})
    if qty <= 0: cart.pop(pid, None)
    else:        cart[pid] = qty
    session['cart'] = cart
    return jsonify({'success': True, 'cart_count': sum(cart.values())})

@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    pid  = str(request.form.get('product_id'))
    cart = session.get('cart', {})
    cart.pop(pid, None)
    session['cart'] = cart
    return jsonify({'success': True, 'cart_count': sum(cart.values())})

@app.route('/cart/count')
def cart_count():
    cart = session.get('cart', {})
    return jsonify({'count': sum(cart.values())})

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart: return redirect(url_for('cart'))
    cart_items = []; total = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    for pid, qty in cart.items():
        cursor.execute("SELECT * FROM products WHERE id=%s", (pid,))
        p = cursor.fetchone()
        if p:
            p['qty']      = qty
            p['subtotal'] = float(p['price']) * qty
            total        += p['subtotal']
            cart_items.append(p)
    if request.method == 'POST':
        step = request.form.get('step')
        if step == 'shipping':
            session['shipping'] = {k: request.form[k] for k in
                ['first_name','last_name','address','city','zip','state','country','phone']}
            conn.close()
            return jsonify({'success': True})
        elif step == 'payment':
            sh      = session.get('shipping', {})
            pm      = request.form.get('payment_method', 'cod')
            ship_c  = 50.0
            tax     = round(total * 0.08, 2)
            grand   = total + ship_c + tax
            # For Razorpay, order is created after payment verification
            if pm == 'razorpay':
                conn.close()
                return jsonify({'success': True, 'razorpay': True, 'amount': grand})
            cursor.execute("""INSERT INTO orders
                (user_id,first_name,last_name,address,city,zip_code,state,country,
                 phone,subtotal,shipping_cost,tax,total,payment_method,status,created_at)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending',NOW())""",
                (session['user_id'], sh.get('first_name',''), sh.get('last_name',''),
                 sh.get('address',''), sh.get('city',''), sh.get('zip',''),
                 sh.get('state',''), sh.get('country',''), sh.get('phone',''),
                 total, ship_c, tax, grand, pm))
            oid = cursor.lastrowid
            for item in cart_items:
                cursor.execute("""INSERT INTO order_items(order_id,product_id,qty,price)
                                  VALUES(%s,%s,%s,%s)""",
                               (oid, item['id'], item['qty'], item['price']))
            # Add notification
            cursor.execute("""INSERT INTO notifications(user_id, title, message, created_at)
                              VALUES(%s, 'Order Placed! 🎉', %s, NOW())""",
                           (session['user_id'], f'Your order #{oid} has been placed successfully. Total: ₹{grand:.0f}'))
            conn.commit()
            session.pop('cart', None); session.pop('shipping', None)
            conn.close()
            return jsonify({'success': True, 'order_id': oid})
    conn.close()
    return render_template('user/checkout.html', cart_items=cart_items, total=total)

@app.route('/orders')
@login_required
def my_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id=%s ORDER BY created_at DESC",
                   (session['user_id'],))
    orders = cursor.fetchall()
    conn.close()
    return render_template('user/orders.html', orders=orders)

@app.route('/order/<int:oid>')
@login_required
def order_detail(oid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id=%s AND user_id=%s", (oid, session['user_id']))
    order = cursor.fetchone()
    if not order:
        conn.close()
        return redirect(url_for('my_orders'))
    cursor.execute("""SELECT oi.*,p.name,p.image FROM order_items oi
                      JOIN products p ON oi.product_id=p.id WHERE oi.order_id=%s""", (oid,))
    items = cursor.fetchall()
    conn.close()
    return render_template('user/order_detail.html', order=order, items=items)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        # FIX #8: Save user address
        first_name = request.form.get('first_name', '')
        last_name  = request.form.get('last_name', '')
        phone      = request.form.get('phone', '')
        address    = request.form.get('address', '')
        city       = request.form.get('city', '')
        state      = request.form.get('state', '')
        zip_code   = request.form.get('zip_code', '')
        cursor.execute("""UPDATE users SET first_name=%s, last_name=%s, phone=%s,
                          address=%s, city=%s, state=%s, zip_code=%s WHERE id=%s""",
                       (first_name, last_name, phone, address, city, state, zip_code,
                        session['user_id']))
        conn.commit()
        session['user_name'] = first_name
        conn.close()
        return jsonify({'success': True, 'message': 'Profile updated!'})
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) as c FROM orders WHERE user_id=%s", (session['user_id'],))
    order_count = cursor.fetchone()['c']
    conn.close()
    return render_template('user/profile.html', user=user, order_count=order_count)

@app.route('/wishlist')
@login_required
def wishlist():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT p.* FROM wishlist w JOIN products p ON w.product_id=p.id
                      WHERE w.user_id=%s""", (session['user_id'],))
    items = cursor.fetchall()
    conn.close()
    return render_template('user/wishlist.html', items=items)

@app.route('/wishlist/toggle', methods=['POST'])
@login_required
def toggle_wishlist():
    pid    = request.form.get('product_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM wishlist WHERE user_id=%s AND product_id=%s",
                   (session['user_id'], pid))
    if cursor.fetchone():
        cursor.execute("DELETE FROM wishlist WHERE user_id=%s AND product_id=%s",
                       (session['user_id'], pid))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'wishlisted': False})
    cursor.execute("INSERT INTO wishlist(user_id,product_id) VALUES(%s,%s)",
                   (session['user_id'], pid))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'wishlisted': True})

# ─────────────────────────────────────────────────────────
#  ADMIN ROUTES
# ─────────────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as c FROM orders");       total_orders   = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM users");        total_users    = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM products");     total_products = cursor.fetchone()['c']
    cursor.execute("SELECT COALESCE(SUM(total),0) as r FROM orders WHERE status!='cancelled'")
    revenue = cursor.fetchone()['r']
    cursor.execute("""SELECT o.*,u.first_name,u.last_name FROM orders o
                      JOIN users u ON o.user_id=u.id ORDER BY o.created_at DESC LIMIT 5""")
    recent_orders = cursor.fetchall()
    cursor.execute("""SELECT DATE(created_at) as date, SUM(total) as total
                      FROM orders WHERE created_at>=DATE_SUB(NOW(),INTERVAL 7 DAY)
                      GROUP BY DATE(created_at) ORDER BY date""")
    sales_data = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) as c FROM orders WHERE status='pending'")
    pending_count = cursor.fetchone()['c']
    conn.close()
    return render_template('admin/dashboard.html',
                           total_orders=total_orders, total_users=total_users,
                           total_products=total_products, revenue=revenue,
                           recent_orders=recent_orders, sales_data=sales_data,
                           pending_count=pending_count)

# ── Admin: save site settings ─────────────────────────────
@app.route('/admin/settings/save', methods=['POST'])
@admin_required
def admin_save_settings():
    data      = request.get_json(force=True) or {}
    hero_title    = data.get('hero_title', '')
    hero_subtitle = data.get('hero_subtitle', '')
    site_name     = data.get('site_name', 'Anas Aatar Wale')
    # FIX #4 Admin: editable service badges
    fast_delivery_title   = data.get('fast_delivery_title', 'Fast Delivery')
    fast_delivery_text    = data.get('fast_delivery_text', '3-5 business days')
    secure_payment_title  = data.get('secure_payment_title', 'Secure Payment')
    secure_payment_text   = data.get('secure_payment_text', '100% safe checkout')
    easy_returns_title    = data.get('easy_returns_title', 'Easy Returns')
    easy_returns_text     = data.get('easy_returns_text', '7 day return policy')
    authentic_title       = data.get('authentic_title', 'Authentic')
    authentic_text        = data.get('authentic_text', '100% genuine product')

    # Save uploaded images (base64 → file)
    hero_image = None
    logo_image = None
    if data.get('hero_image_data'):
        hero_image = save_base64_image(data['hero_image_data'], 'hero')
    if data.get('logo_image_data'):
        logo_image = save_base64_image(data['logo_image_data'], 'logo')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM site_settings LIMIT 1")
    existing = cursor.fetchone()

    if existing:
        sets = """hero_title=%s, hero_subtitle=%s, site_name=%s,
                  fast_delivery_title=%s, fast_delivery_text=%s,
                  secure_payment_title=%s, secure_payment_text=%s,
                  easy_returns_title=%s, easy_returns_text=%s,
                  authentic_title=%s, authentic_text=%s, updated_at=NOW()"""
        vals = [hero_title, hero_subtitle, site_name,
                fast_delivery_title, fast_delivery_text,
                secure_payment_title, secure_payment_text,
                easy_returns_title, easy_returns_text,
                authentic_title, authentic_text]
        if hero_image: sets += ", hero_image=%s"; vals.append(hero_image)
        if logo_image: sets += ", logo_image=%s"; vals.append(logo_image)
        cursor.execute(f"UPDATE site_settings SET {sets} WHERE id=%s",
                       vals + [existing['id']])
    else:
        cursor.execute("""INSERT INTO site_settings
            (hero_title,hero_subtitle,site_name,hero_image,logo_image,
             fast_delivery_title,fast_delivery_text,secure_payment_title,secure_payment_text,
             easy_returns_title,easy_returns_text,authentic_title,authentic_text,updated_at)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())""",
            (hero_title, hero_subtitle, site_name, hero_image or '', logo_image or '',
             fast_delivery_title, fast_delivery_text, secure_payment_title, secure_payment_text,
             easy_returns_title, easy_returns_text, authentic_title, authentic_text))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── Admin: Products ───────────────────────────────────────
@app.route('/admin/products')
@admin_required
def admin_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT p.*,c.name as category_name FROM products p
                      LEFT JOIN categories c ON p.category_id=c.id ORDER BY p.created_at DESC""")
    products   = cursor.fetchall()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    conn.close()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/products/add', methods=['POST'])
@admin_required
def admin_add_product():
    try:
        # FIX: Accept both JSON and FormData
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json(force=True) or {}
            image = save_base64_image(data.get('image_data'), 'product') or ''
            name = data.get('name', '')
            description = data.get('description', '')
            price = data.get('price', 0)
            category_id = data.get('category_id', 1)
            stock = data.get('stock', 0)
            rating = data.get('rating', 4.0)
            volume = data.get('volume', '')
        else:
            data = request.form
            name = data.get('name', '')
            description = data.get('description', '')
            price = data.get('price', 0)
            category_id = data.get('category_id', 1)
            stock = data.get('stock', 0)
            rating = data.get('rating', 4.0)
            volume = data.get('volume', '')
            # Handle file upload
            image = ''
            img_data = data.get('image_data', '')
            if img_data:
                image = save_base64_image(img_data, 'product') or ''

        if not name or not price:
            return jsonify({'success': False, 'error': 'Name and price required'}), 400
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO products
            (name,description,price,category_id,stock,rating,volume,image,is_active,created_at)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,1,NOW())""",
            (name, description, price, category_id, stock, rating, volume, image))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# FIX #1 Admin: Products edit — properly handle both image & data
@app.route('/admin/products/edit/<int:pid>', methods=['POST'])
@admin_required
def admin_edit_product(pid):
    try:
        # FIX: Accept both JSON and FormData
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json(force=True) or {}
            image_data = data.get('image_data')
        else:
            data = request.form
            image_data = data.get('image_data', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Image-only update
        if data.get('_imageOnly'):
            image = save_base64_image(image_data, 'product')
            if image:
                cursor.execute("UPDATE products SET image=%s WHERE id=%s", (image, pid))
                conn.commit()
            conn.close()
            return jsonify({'success': True})

        # Full update — use existing values as fallback
        cursor.execute("SELECT * FROM products WHERE id=%s", (pid,))
        ex = cursor.fetchone() or {}

        name        = data.get('name')        or ex.get('name','')
        description = data.get('description') or ex.get('description','')
        price       = data.get('price')       or ex.get('price',0)
        category_id = data.get('category_id') or ex.get('category_id',1)
        stock       = data.get('stock',       ex.get('stock',0))
        rating      = data.get('rating',      ex.get('rating',4.0))
        volume      = data.get('volume')      or ex.get('volume','')
        is_active   = data.get('is_active',   ex.get('is_active',1))

        sets = "name=%s,description=%s,price=%s,category_id=%s,stock=%s,rating=%s,volume=%s,is_active=%s"
        vals = [name,description,price,category_id,stock,rating,volume,is_active]

        # Only update image if new one is provided
        image = save_base64_image(image_data, 'product')
        if image:
            sets += ",image=%s"; vals.append(image)

        cursor.execute(f"UPDATE products SET {sets} WHERE id=%s", vals + [pid])
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Edit product error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/products/delete/<int:pid>', methods=['POST'])
@admin_required
def admin_delete_product(pid):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Remove from wishlists and order items first
        cursor.execute("DELETE FROM wishlist WHERE product_id=%s", (pid,))
        cursor.execute("DELETE FROM product_reviews WHERE product_id=%s", (pid,))
        cursor.execute("DELETE FROM products WHERE id=%s", (pid,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ── Admin: Orders ─────────────────────────────────────────
@app.route('/admin/orders')
@admin_required
def admin_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT o.*,u.first_name,u.last_name,u.email FROM orders o
                      JOIN users u ON o.user_id=u.id ORDER BY o.created_at DESC""")
    orders = cursor.fetchall()
    conn.close()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/orders/status/<int:oid>', methods=['POST'])
@admin_required
def admin_update_order_status(oid):
    status = request.form.get('status') or (request.get_json(force=True) or {}).get('status')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM orders WHERE id=%s", (oid,))
    order = cursor.fetchone()
    cursor.execute("UPDATE orders SET status=%s WHERE id=%s", (status, oid))
    # Notify user of status change
    if order:
        status_msgs = {
            'confirmed': f'Your order #{oid} has been confirmed! ✅',
            'processing': f'Your order #{oid} is being processed 🔄',
            'shipped': f'Your order #{oid} has been shipped! 🚚',
            'delivered': f'Your order #{oid} has been delivered! 🎉',
            'cancelled': f'Your order #{oid} has been cancelled ❌'
        }
        if status in status_msgs:
            cursor.execute("""INSERT INTO notifications(user_id, title, message, created_at)
                              VALUES(%s, 'Order Update', %s, NOW())""",
                           (order['user_id'], status_msgs[status]))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── Admin: Users ──────────────────────────────────────────
@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT u.*,COUNT(o.id) as order_count FROM users u
                      LEFT JOIN orders o ON u.id=o.user_id GROUP BY u.id
                      ORDER BY u.created_at DESC""")
    users = cursor.fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

# FIX #2 Admin: Categories — add delete + edit
@app.route('/admin/categories')
@admin_required
def admin_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT c.*,COUNT(p.id) as product_count FROM categories c
                      LEFT JOIN products p ON c.id=p.category_id GROUP BY c.id""")
    categories = cursor.fetchall()
    conn.close()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/save', methods=['POST'])
@admin_required
def admin_save_category():
    data   = request.get_json(force=True) or {}
    cid    = data.get('id')
    name   = data.get('name','')
    icon   = data.get('icon','🏷️')
    if not name.strip():
        return jsonify({'success': False, 'error': 'Name required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    if cid:
        cursor.execute("UPDATE categories SET name=%s,icon=%s WHERE id=%s", (name, icon, cid))
    else:
        cursor.execute("INSERT INTO categories(name,icon) VALUES(%s,%s)", (name, icon))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# FIX #2 Admin: Delete category
@app.route('/admin/categories/delete/<int:cid>', methods=['POST'])
@admin_required
def admin_delete_category(cid):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if any products use this category
    cursor.execute("SELECT COUNT(*) as c FROM products WHERE category_id=%s", (cid,))
    count = cursor.fetchone()['c']
    if count > 0:
        conn.close()
        return jsonify({'success': False, 'error': f'Cannot delete: {count} products use this category. Reassign them first.'}), 400
    cursor.execute("DELETE FROM categories WHERE id=%s", (cid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None); session.pop('admin_name', None)
    return redirect(url_for('login') + '?admin=1')

# ── Context processor: inject settings into ALL templates ──
@app.context_processor
def inject_globals():
    settings = {}
    try:
        settings = get_site_settings()
        settings.pop('updated_at', None)
    except Exception:
        settings = {
            'hero_title': 'Discover Your <span>Signature</span> Fragrance',
            'hero_subtitle': 'Handcrafted attars and perfumes.',
            'hero_image': '', 'logo_image': '',
            'site_name': 'Anas Aatar Wale',
            'fast_delivery_title': 'Fast Delivery',
            'fast_delivery_text': '3-5 business days',
            'secure_payment_title': 'Secure Payment',
            'secure_payment_text': '100% safe checkout',
            'easy_returns_title': 'Easy Returns',
            'easy_returns_text': '7 day return policy',
            'authentic_title': 'Authentic',
            'authentic_text': '100% genuine product',
        }
    cart = session.get('cart', {})
    return dict(
        settings=settings,
        cart_count=sum(cart.values()),
        is_admin='admin_id' in session
    )

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1')
