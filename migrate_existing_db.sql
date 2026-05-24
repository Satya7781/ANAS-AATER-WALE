-- =============================================
-- MIGRATION: Run this if you already have the
-- anas_aatar_db and want to add the new tables/columns
-- =============================================
USE anas_aatar_db;

-- FIX #8: Add address columns to users table
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS address TEXT,
  ADD COLUMN IF NOT EXISTS city VARCHAR(100),
  ADD COLUMN IF NOT EXISTS state VARCHAR(100),
  ADD COLUMN IF NOT EXISTS zip_code VARCHAR(20);

-- FIX #4 User: product reviews table
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

-- FIX #6: notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- FIX #4 Admin: add service badge columns to site_settings
ALTER TABLE site_settings
  ADD COLUMN IF NOT EXISTS fast_delivery_title VARCHAR(100) DEFAULT 'Fast Delivery',
  ADD COLUMN IF NOT EXISTS fast_delivery_text VARCHAR(200) DEFAULT '3-5 business days',
  ADD COLUMN IF NOT EXISTS secure_payment_title VARCHAR(100) DEFAULT 'Secure Payment',
  ADD COLUMN IF NOT EXISTS secure_payment_text VARCHAR(200) DEFAULT '100% safe checkout',
  ADD COLUMN IF NOT EXISTS easy_returns_title VARCHAR(100) DEFAULT 'Easy Returns',
  ADD COLUMN IF NOT EXISTS easy_returns_text VARCHAR(200) DEFAULT '7 day return policy',
  ADD COLUMN IF NOT EXISTS authentic_title VARCHAR(100) DEFAULT 'Authentic',
  ADD COLUMN IF NOT EXISTS authentic_text VARCHAR(200) DEFAULT '100% genuine product';

SELECT 'Migration complete!' as status;
