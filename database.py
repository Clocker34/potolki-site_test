import sqlite3

def get_db():
    conn = sqlite3.connect('potolki.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            unit TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            area REAL,
            service_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Заполним тестовыми данными если таблица пустая
    cursor.execute('SELECT COUNT(*) FROM services')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO services (name, price, unit) VALUES (?, ?, ?)', [
            ('Натяжное полотно (белое)', 350, 'м²'),
            ('Натяжное полотно (цветное)', 520, 'м²'),
            ('Монтаж потолка', 200, 'м²'),
            ('Демонтаж старого потолка', 100, 'м²'),
            ('Установка светильника', 300, 'шт'),
        ])

    cursor.execute('SELECT COUNT(*) FROM portfolio')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO portfolio (title, description, date) VALUES (?, ?, ?)', [
            ('Квартира на Тверской', '3-комнатная квартира, белые матовые потолки', '2026-01-15'),
            ('Офис в бизнес-центре', 'Натяжные потолки с подсветкой, 200 м²', '2026-02-10'),
            ('Частный дом в Подмосковье', 'Цветные полотна в детской комнате', '2026-03-01'),
        ])

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('База данных создана!')
