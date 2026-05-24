def seed_data():
import pymysql

# Database connection configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',
    'database': 'anas_aatar_db',
    'charset': 'utf8mb4'
}

def seed_data():
    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # Insert categories
        categories = [
            ('Oud','🪵'),('Floral','🌸'),('Musk','🌿'),
            ('Citrus','🍋'),('Oriental','🌙'),('Rose','🌹')
        ]
        
        cursor.executemany("INSERT IGNORE INTO categories (name, icon) VALUES (%s, %s)", categories)
        
        # Insert products (after categories exist)
        products = [
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
            ('Oud Sultani','Sultan-inspired oud blend with deep resinous heart and lasting power.',1899.00,1,15,4.8,'15ml')
        ]
        
        cursor.executemany("""INSERT IGNORE INTO products 
            (name,description,price,category_id,stock,rating,volume) 
            VALUES (%s,%s,%s,%s,%s,%s,%s)""", products)
        
        # Insert site settings
        cursor.execute("""INSERT IGNORE INTO site_settings 
            (site_name,hero_title,hero_subtitle) 
            VALUES (%s,%s,%s)""", (
            'Anas Aatar Wale',
            'Discover Your <span>Signature</span> Fragrance',
            'Handcrafted attars and perfumes made with the finest natural ingredients. Experience the art of ancient perfumery blended with modern elegance.'
        ))
        
        # Insert admin user (password: admin123)
        import hashlib
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute("INSERT IGNORE INTO admins (username,password) VALUES (%s,%s)", ('admin', admin_password))
        
        # Insert regular user (password: user123)
        user_password = hashlib.sha256('user123'.encode()).hexdigest()
        cursor.execute("""INSERT IGNORE INTO users 
            (first_name,last_name,email,password,phone) 
            VALUES (%s,%s,%s,%s,%s)""", 
            ('Anas','Khan','anas@example.com', user_password, '+91 9876543210'))
        
        connection.commit()
        print("Seed data inserted successfully!")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error seeding data: {e}")

if __name__ == "__main__":
    seed_data()

if __name__ == "__main__":
    seed_data()
