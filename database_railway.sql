-- =============================================
-- Anas Aatar Wale v3 - Database Schema for Railway
-- NOTE: Railway uses 'railway' as default database
-- =============================================

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(10) DEFAULT '*',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INT,
    stock INT DEFAULT 0,
    rating DECIMAL(3,1) DEFAULT 4.0,
    volume VARCHAR(50),
    image VARCHAR(500) DEFAULT '',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(64) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS site_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site_name VARCHAR(200) DEFAULT 'Anas Aatar Wale',
    hero_title TEXT,
    hero_subtitle TEXT,
    hero_image VARCHAR(500) DEFAULT '',
    logo_image VARCHAR(500) DEFAULT '',
    fast_delivery_title VARCHAR(100) DEFAULT 'Fast Delivery',
    fast_delivery_text VARCHAR(200) DEFAULT '3-5 business days',
    secure_payment_title VARCHAR(100) DEFAULT 'Secure Payment',
    secure_payment_text VARCHAR(200) DEFAULT '100% safe checkout',
    easy_returns_title VARCHAR(100) DEFAULT 'Easy Returns',
    easy_returns_text VARCHAR(200) DEFAULT '7 day return policy',
    authentic_title VARCHAR(100) DEFAULT 'Authentic',
    authentic_text VARCHAR(200) DEFAULT '100% genuine product',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    first_name VARCHAR(100), last_name VARCHAR(100),
    address TEXT, city VARCHAR(100), zip_code VARCHAR(20),
    state VARCHAR(100), country VARCHAR(100), phone VARCHAR(20),
    subtotal DECIMAL(10,2), shipping_cost DECIMAL(10,2) DEFAULT 50.00,
    tax DECIMAL(10,2) DEFAULT 0.00, total DECIMAL(10,2),
    payment_method ENUM('cod','online','upi') DEFAULT 'cod',
    status ENUM('pending','confirmed','processing','shipped','delivered','cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL, product_id INT NOT NULL,
    qty INT DEFAULT 1, price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL, product_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_wishlist (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS product_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL DEFAULT 5,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_review (user_id, product_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── SEED DATA ───────────────────────────────────────────
INSERT INTO categories (name, icon) VALUES
('Oud','*'),('Floral','*'),('Musk','*'),
('Citrus','*'),('Oriental','*'),('Rose','*');

INSERT INTO products (name,description,price,category_id,stock,rating,volume) VALUES
('Oud Al Layl','A rich smoky oud attar with deep woody notes that linger for hours.',1299.00,1,50,4.8,'12ml'),
('Rose Taifi','Pure rose attar extracted from finest Taif roses. Delicate and long-lasting.',899.00,6,40,4.7,'10ml'),
('Musk Al Abiyad','White musk attar with soft, clean and powdery notes.',699.00,3,60,4.5,'12ml'),
('Amber Noir','Rich amber attar with vanilla and sandalwood base. Warm and enchanting.',1199.00,5,35,4.6,'8ml'),
('Jasmine Breeze','Fresh jasmine attar with light floral notes. Perfect for daytime.',799.00,2,45,4.4,'10ml'),
('Oud Malaki','Royal oud blend with premium ingredients. An exclusive fragrance.',2499.00,1,20,4.9,'15ml'),
('Citrus Fresh','Zesty citrus attar with lemon, bergamot and orange notes.',599.00,4,70,4.3,'10ml'),
('Oud Bakhoor','Traditional bakhoor-inspired attar. Warm smoky incense with precious oud.',1599.00,1,25,4.7,'12ml'),
('Floral Harmony','A beautiful bouquet of mixed florals — rose, jasmine and ylang ylang.',749.00,2,55,4.5,'10ml'),
('Oriental Dream','A luxurious oriental blend with spices, resins and precious woods.',1099.00,5,30,4.6,'12ml'),
('Musk Tahara','Pure halal musk with a clean, fresh and slightly sweet scent.',849.00,3,50,4.4,'10ml'),
('Oud Sultani','Sultan-inspired oud blend with deep resinous heart and lasting power.',1899.00,1,15,4.8,'15ml');

INSERT INTO site_settings (site_name,hero_title,hero_subtitle) VALUES
('Anas Aatar Wale',
 'Discover Your <span>Signature</span> Fragrance',
 'Handcrafted attars and perfumes made with the finest natural ingredients. Experience the art of ancient perfumery blended with modern elegance.');

INSERT INTO admins (username,password) VALUES ('admin', SHA2('admin123',256));
INSERT INTO users (first_name,last_name,email,password,phone) VALUES
('Anas','Khan','anas@example.com', SHA2('user123',256), '+91 9876543210');
