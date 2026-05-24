def create_site_settings_table():
import pymysql

# Database connection configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',
    'database': 'anas_aatar_db',
    'charset': 'utf8mb4'
}

def create_site_settings_table():
    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # Create site_settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS site_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                site_name VARCHAR(200) DEFAULT 'Anas Aatar Wale',
                hero_title TEXT,
                hero_subtitle TEXT,
                hero_image VARCHAR(500) DEFAULT '',
                logo_image VARCHAR(500) DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default settings
        cursor.execute("""
            INSERT IGNORE INTO site_settings 
            (site_name,hero_title,hero_subtitle) 
            VALUES (%s,%s,%s)
        """, (
            'Anas Aatar Wale',
            'Discover Your <span>Signature</span> Fragrance',
            'Handcrafted attars and perfumes made with the finest natural ingredients. Experience the art of ancient perfumery blended with modern elegance.'
        ))
        
        connection.commit()
        print("site_settings table created and seeded successfully!")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error creating site_settings table: {e}")

if __name__ == "__main__":
    create_site_settings_table()

if __name__ == "__main__":
    create_site_settings_table()
