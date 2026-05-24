def create_database():
import pymysql
import sys

# Database connection configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',
    'charset': 'utf8mb4'
}

def create_database():
    try:
        # Connect to MySQL without specifying database
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS anas_aatar_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("Database 'anas_aatar_db' created successfully!")
        
        # Switch to the created database
        cursor.execute("USE anas_aatar_db")
        
        # Read and execute the SQL schema
        with open('database.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Remove the CREATE DATABASE and USE statements since we already handled them
        lines = sql_content.split('\n')
        filtered_lines = []
        skip_lines = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('CREATE DATABASE') or line.startswith('USE anas_aatar_db'):
                continue
            filtered_lines.append(line)
        
        sql_content = '\n'.join(filtered_lines)
        
        # Split the SQL content into individual statements
        statements = sql_content.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    connection.commit()
                except Exception as e:
                    print(f"Warning: Could not execute statement: {statement[:50]}... Error: {e}")
                    # Continue with other statements
        
        connection.commit()
        print("Database schema and seed data imported successfully!")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()

if __name__ == "__main__":
    create_database()
