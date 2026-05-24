def check_tables():
import pymysql

# Database connection configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',
    'database': 'anas_aatar_db',
    'charset': 'utf8mb4'
}

def check_tables():
    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # Show all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"- {table[0]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error checking tables: {e}")

if __name__ == "__main__":
    check_tables()

if __name__ == "__main__":
    check_tables()
