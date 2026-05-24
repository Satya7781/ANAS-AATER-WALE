from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Sequence


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "anas_aatar_db.sqlite3"


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        icon TEXT DEFAULT '🌸',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        price REAL NOT NULL,
        category_id INTEGER,
        stock INTEGER DEFAULT 0,
        rating REAL DEFAULT 4.0,
        volume TEXT,
        image TEXT DEFAULT '',
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS site_settings (
        id INTEGER PRIMARY KEY,
        site_name TEXT DEFAULT 'Anas Aatar Wale',
        hero_title TEXT DEFAULT 'Discover Your <span>Signature</span> Fragrance',
        hero_subtitle TEXT DEFAULT 'Handcrafted attars and perfumes made with the finest natural ingredients.',
        hero_image TEXT DEFAULT '',
        logo_image TEXT DEFAULT '',
        fast_delivery_title TEXT DEFAULT 'Fast Delivery',
        fast_delivery_text TEXT DEFAULT '3-5 business days',
        secure_payment_title TEXT DEFAULT 'Secure Payment',
        secure_payment_text TEXT DEFAULT '100% safe checkout',
        easy_returns_title TEXT DEFAULT 'Easy Returns',
        easy_returns_text TEXT DEFAULT '7 day return policy',
        authentic_title TEXT DEFAULT 'Authentic',
        authentic_text TEXT DEFAULT '100% genuine product',
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        first_name TEXT,
        last_name TEXT,
        address TEXT,
        city TEXT,
        zip_code TEXT,
        state TEXT,
        country TEXT,
        phone TEXT,
        subtotal REAL,
        shipping_cost REAL DEFAULT 50.00,
        tax REAL DEFAULT 0.00,
        total REAL,
        payment_method TEXT DEFAULT 'cod',
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        qty INTEGER DEFAULT 1,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (user_id, product_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS product_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL DEFAULT 5,
        comment TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (user_id, product_id),
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_site_settings_updated_at
    AFTER UPDATE ON site_settings
    FOR EACH ROW
    BEGIN
        UPDATE site_settings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    """,
]


CATEGORY_SEED = [
    ("Oud", "🪵"),
    ("Floral", "🌸"),
    ("Musk", "🌿"),
    ("Citrus", "🍋"),
    ("Oriental", "🌙"),
    ("Rose", "🌹"),
]

PRODUCT_SEED = [
    ("Oud Al Layl", "A rich smoky oud attar with deep woody notes that linger for hours.", 1299.00, 1, 50, 4.8, "12ml"),
    ("Rose Taifi", "Pure rose attar extracted from finest Taif roses. Delicate and long-lasting.", 899.00, 6, 40, 4.7, "10ml"),
    ("Musk Al Abiyad", "White musk attar with soft, clean and powdery notes.", 699.00, 3, 60, 4.5, "12ml"),
    ("Amber Noir", "Rich amber attar with vanilla and sandalwood base. Warm and enchanting.", 1199.00, 5, 35, 4.6, "8ml"),
    ("Jasmine Breeze", "Fresh jasmine attar with light floral notes. Perfect for daytime.", 799.00, 2, 45, 4.4, "10ml"),
    ("Oud Malaki", "Royal oud blend with premium ingredients. An exclusive fragrance.", 2499.00, 1, 20, 4.9, "15ml"),
    ("Citrus Fresh", "Zesty citrus attar with lemon, bergamot and orange notes.", 599.00, 4, 70, 4.3, "10ml"),
    ("Oud Bakhoor", "Traditional bakhoor-inspired attar. Warm smoky incense with precious oud.", 1599.00, 1, 25, 4.7, "12ml"),
    ("Floral Harmony", "A beautiful bouquet of mixed florals — rose, jasmine and ylang ylang.", 749.00, 2, 55, 4.5, "10ml"),
    ("Oriental Dream", "A luxurious oriental blend with spices, resins and precious woods.", 1099.00, 5, 30, 4.6, "12ml"),
    ("Musk Tahara", "Pure halal musk with a clean, fresh and slightly sweet scent.", 849.00, 3, 50, 4.4, "10ml"),
    ("Oud Sultani", "Sultan-inspired oud blend with deep resinous heart and lasting power.", 1899.00, 1, 15, 4.8, "15ml"),
]


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _translate_sql(sql: str) -> str:
    return sql.replace("%s", "?")


class SQLiteCursorWrapper:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    def execute(self, sql: str, params: Sequence | None = None):
        if params is None:
            return self._cursor.execute(sql)
        return self._cursor.execute(_translate_sql(sql), params)

    def executemany(self, sql: str, seq_of_params: Iterable[Sequence]):
        return self._cursor.executemany(_translate_sql(sql), seq_of_params)

    def fetchone(self):
        row = self._cursor.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        return [dict(row) for row in self._cursor.fetchall()]

    def close(self):
        return self._cursor.close()

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class SQLiteConnectionWrapper:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def cursor(self):
        return SQLiteCursorWrapper(self._connection.cursor())

    def commit(self):
        return self._connection.commit()

    def close(self):
        return self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.commit()
        self.close()

    def __getattr__(self, name):
        return getattr(self._connection, name)


def init_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as connection:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)

        cursor = SQLiteCursorWrapper(connection.cursor())

        cursor.execute("SELECT COUNT(*) AS c FROM categories")
        if cursor.fetchone()["c"] == 0:
            cursor.executemany("INSERT INTO categories (name, icon) VALUES (%s, %s)", CATEGORY_SEED)

        cursor.execute("SELECT COUNT(*) AS c FROM products")
        if cursor.fetchone()["c"] == 0:
            cursor.executemany(
                """INSERT INTO products
                (name, description, price, category_id, stock, rating, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                PRODUCT_SEED,
            )

        cursor.execute("SELECT COUNT(*) AS c FROM site_settings")
        if cursor.fetchone()["c"] == 0:
            cursor.execute(
                """INSERT INTO site_settings
                (id, site_name, hero_title, hero_subtitle)
                VALUES (%s, %s, %s, %s)""",
                (
                    1,
                    "Anas Aatar Wale",
                    "Discover Your <span>Signature</span> Fragrance",
                    "Handcrafted attars and perfumes made with the finest natural ingredients. Experience the art of ancient perfumery blended with modern elegance.",
                ),
            )

        cursor.execute("SELECT COUNT(*) AS c FROM admins")
        if cursor.fetchone()["c"] == 0:
            cursor.execute(
                "INSERT INTO admins (username, password) VALUES (%s, %s)",
                ("admin", "e54fc6b51915e222ba6196747a19ebb8dfa651fd2b46a385a0ded647fbfefda0"),
            )

        cursor.execute("SELECT COUNT(*) AS c FROM users")
        if cursor.fetchone()["c"] == 0:
            cursor.execute(
                """INSERT INTO users
                (first_name, last_name, email, password, phone)
                VALUES (%s, %s, %s, %s, %s)""",
                ("Anas", "Khan", "anas@example.com", "e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446", "+91 9876543210"),
            )

        connection.commit()


def get_db_connection() -> SQLiteConnectionWrapper:
    init_database()
    return SQLiteConnectionWrapper(_connect())


def list_tables() -> list[str]:
    init_database()
    with _connect() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
