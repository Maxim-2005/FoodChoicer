import sqlite3
import threading
from typing import List, Tuple

class Database:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_db()
        return cls._instance
    
    def _init_db(self):
        self.conn = sqlite3.connect('dishes.db', check_same_thread=False)
        self._create_tables()
        self._insert_default_data()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            UNIQUE(name, category_id)
        )''')
        self.conn.commit()
    
    def _insert_default_data(self):
        default_categories = ['Завтрак', 'Обед', 'Ужин']
        cursor = self.conn.cursor()
        for category in default_categories:
            try:
                cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
            except sqlite3.IntegrityError:
                pass
        self.conn.commit()
    
    def add_dish(self, category_name: str, dish_name: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            category_id = cursor.fetchone()[0]
            
            cursor.execute('INSERT INTO dishes (name, category_id) VALUES (?, ?)', 
                         (dish_name, category_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error adding dish: {e}")
            return False

    def remove_dish(self, category_name: str, dish_name: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            category_id = cursor.fetchone()[0]
            
            cursor.execute('DELETE FROM dishes WHERE name = ? AND category_id = ?', 
                         (dish_name, category_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing dish: {e}")
            self.conn.rollback()
            return False

    def get_dishes(self, category_name: str) -> List[Tuple[int, str]]:
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT d.id, d.name 
        FROM dishes d
        JOIN categories c ON d.category_id = c.id
        WHERE c.name = ?
        ORDER BY d.name
        ''', (category_name,))
        return cursor.fetchall()

    def get_all_categories(self) -> List[Tuple[int, str]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name FROM categories ORDER BY name')
        return cursor.fetchall()

    def close(self):
        self.conn.close()