import sqlite3

conn = sqlite3.connect("orders.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    product_name TEXT,
    status TEXT
)
""")

cursor.executemany("""
INSERT INTO orders (customer_name, product_name, status)
VALUES (?, ?, ?)
""", [
    ("Ali", "Nike Air Force 1 Mid '07", "Shipped"),
    ("Sara", "Adidas Ultraboost 22", "Processing"),
    ("John", "Puma Running Shoes", "Delivered"),
    ("Emma", "Reebok Classic Leather", "Cancelled")
])

conn.commit()
conn.close()

print(" Db done")
