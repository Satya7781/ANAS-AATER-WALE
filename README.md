# Anas Aatar Wale v3 - Fixed Edition

## 🔧 ALL BUGS FIXED

### User Side
1. ✅ **Images now show** — logo and product images display correctly
2. ✅ **Category filter works** — clicking a category shows only its products
3. ✅ **Product Reviews** — users can rate (1-5 stars) and write feedback on product pages
4. ✅ **Login back-button fixed** — browser back button won't return to login page
5. ✅ **Notification bell** — real-time order status notifications in navbar
6. ✅ **Order status animation** — step-by-step stepper (Pending→Confirmed→Processing→Shipped→Delivered)
7. ✅ **User address saved** — full address management in profile page

### Database
8. ✅ **Passwords secure** — stored as SHA-256 hash (e54fc6b51... = hashed version of your password, this is CORRECT and safe). Plain text passwords are NEVER stored.
   - `admin123` → stored as SHA256 hash
   - `user123` → stored as SHA256 hash

### Admin Side
9. ✅ **Edit products works** — name, price, stock, category, image all save correctly
10. ✅ **Category delete + edit** — full CRUD on categories with product-count guard
11. ✅ **Product image upload fixed** — simple file input, no more foreign key error
12. ✅ **Edit Fast Delivery / Easy Returns** — in Hero Editor → Service Badges section
13. ✅ **Admin notifications** — bell shows pending order count and recent orders list

---

## 🚀 Setup Instructions

### Fresh Install (New Database)
```bash
# 1. Import fresh database
mysql -u root -p < database.sql

# 2. Install requirements
pip install -r requirements.txt

# 3. Run
python app.py
```

### Existing Database (Migration)
```bash
# 1. Run migration to add new columns/tables
mysql -u root -p anas_aatar_db < migrate_existing_db.sql

# 2. Run app
python app.py
```

### Default Credentials
- **Admin:** username `admin` / password `admin123`
- **User:** email `anas@example.com` / password `user123`

---

## 📁 File Structure
```
anas_aatar_v3/
├── app.py                    ← Main Flask app (all routes fixed)
├── database.sql              ← Fresh database with all tables
├── migrate_existing_db.sql   ← Run this on existing databases
├── requirements.txt
├── static/
│   ├── css/style.css
│   ├── css/admin.css
│   ├── js/main.js
│   ├── js/realtime.js
│   ├── js/admin_inline.js
│   ├── js/cropper_util.js
│   ├── img/01.png            ← Logo image (FIX: moved to static/)
│   └── uploads/              ← Product/hero images saved here
└── templates/
    ├── user/
    │   ├── base.html         ← Notification bell added
    │   ├── index.html        ← Service badges from DB
    │   ├── login.html        ← No back-button issue
    │   ├── orders.html       ← Animated order stepper
    │   ├── product_detail.html ← Reviews section added
    │   └── profile.html      ← Address management
    └── admin/
        ├── base.html         ← Real notification panel
        ├── products.html     ← Edit/image upload fixed
        └── categories.html   ← Edit + Delete added
```

## ⚠️ About Password Hashing
The hash `e54fc6b51915e222ba6196747a19ebb8dfa651fd2b46a385a0ded647fbfefda0` is the **SHA-256 hash of `admin123`**.
This is **correct security** — never store plain text passwords.
To log in, just type your normal password (`admin123`) and it gets hashed before comparing.
# ANAS-AATER-WALE

## Render deployment
Render does not provide a local MySQL server at `localhost`, so set these environment variables on the web service:

- `MYSQL_HOST`: your remote MySQL host
- `MYSQL_PORT`: usually `3306`
- `MYSQL_USER`: your MySQL username
- `MYSQL_PASSWORD`: your MySQL password
- `MYSQL_DB`: the database name, usually `anas_aatar_db`

Use a remote MySQL provider or a managed database that Render can reach over the network.
