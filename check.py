import sqlite3

conn = sqlite3.connect("invoices.db")
cursor = conn.cursor()

print("--- INVOICES ---")
cursor.execute("SELECT * FROM invoices")
invoices = cursor.fetchall()
for invoice in invoices:
    print(invoice)

print("\n--- ITEMS ---")
cursor.execute("SELECT * FROM items")
items = cursor.fetchall()
for item in items:
    print(item)

conn.close()