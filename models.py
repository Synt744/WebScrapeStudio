from dataclasses import dataclass
from datetime import datetime
import sqlite3
from typing import List, Optional

@dataclass
class ScrapingConfig:
    url_pattern: str
    selectors: dict
    use_selenium: bool = False
    headers: Optional[dict] = None
    proxy: Optional[str] = None
    handle_cloudflare: bool = False
    captcha_api_key: Optional[str] = None
    captcha_site_key: Optional[str] = None

@dataclass
class Product:
    id: Optional[int]
    name: str
    price: float
    description: str
    url: str
    marketplace: str
    created_at: datetime

    @staticmethod
    def create_table(conn: sqlite3.Connection):
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            url TEXT NOT NULL,
            marketplace TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()

    def save(self, conn: sqlite3.Connection):
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO products (name, price, description, url, marketplace, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.name, self.price, self.description, self.url, self.marketplace,
              self.created_at))
        conn.commit()
        self.id = cursor.lastrowid

    @staticmethod
    def get_all(conn: sqlite3.Connection) -> List['Product']:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products')
        rows = cursor.fetchall()
        return [Product(
            id=row[0],
            name=row[1],
            price=row[2],
            description=row[3],
            url=row[4],
            marketplace=row[5],
            created_at=datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S')
        ) for row in rows]