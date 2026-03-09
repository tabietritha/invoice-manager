import sqlite3

def init_db():
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    
    # Create invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            client_name TEXT,
            total REAL,
            date TEXT,
            status TEXT DEFAULT 'Unpaid'
        )
    ''')
    
    # Create items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            description TEXT,
            quantity INTEGER,
            price REAL,
            subtotal REAL,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')
    # products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL
    )
''')
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

init_db()