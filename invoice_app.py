from flask import Flask, redirect, render_template, request, session,jsonify
import sqlite3


def save_invoice(invoice_number, client_name, total, invoice_date, items, status, product_ids):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()

    # Save invoice
    cursor.execute(
        """
        INSERT INTO invoices (invoice_number, client_name, total, date,status)
        VALUES (?, ?, ?, ?, ?)
    """,
        (invoice_number, client_name, total, invoice_date, status),
    )

    # Get invoice id
    invoice_id = cursor.lastrowid

    # Save each item
    for i, item in enumerate(items):
        cursor.execute(
            """
            INSERT INTO items (invoice_id, description, quantity, price, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                invoice_id,
                item["description"],
                item["quantity"],
                item["price"],
                item["total"],
            ),
        )
        
        if i < len(product_ids) and product_ids[i]:
            cursor.execute(
                """
                UPDATE products SET quantity = quantity - ? WHERE id = ?
                """,
                (item["quantity"], product_ids[i])
            )

    conn.commit()
    conn.close()


app = Flask(__name__)
app.secret_key = "your_secret_key"
INVENTORY_PASSWORD = "0700" 
ADMIN_PASSWORD = "admin0700"


@app.route("/")
def home():
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template("index.html", products=products)


@app.route("/generate", methods=["POST"])
def generate_invoice():
    import random
    from datetime import date

    invoice_number = random.randint(1000, 9999)
    invoice_date = date.today().strftime("%Y-%m-%d")

    # get the form data
    client_name = request.form["client_name"]
    item_descriptions = request.form.getlist("item_description[]")
    item_quantity = request.form.getlist("item_quantity[]")
    item_price = request.form.getlist("item_price[]")
    status = request.form.get("status", "Unpaid")  
    product_ids = request.form.getlist("product_id[]")  # Get product IDs from the form

    # calculate total
    items = []
    total = 0

    for i in range(len(item_descriptions)):

        quantity = int(item_quantity[i])
        price = float(item_price[i])
        item_total = quantity * price
        total += item_total

        items.append(
            {
                "description": item_descriptions[i],
                "quantity": quantity,
                "price": price,
                "total": item_total,
            }
        )

    # save the invoice to the database
    save_invoice(invoice_number, client_name, total, invoice_date, items, status, product_ids)

    # render the invoice template with the data
    return render_template(
        "invoice.html",
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        client_name=client_name,
        items=items,
        total=total,
    )


@app.route("/tracker")
def tracker():
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()

    # get all invoices
    cursor.execute(
        "SELECT id, invoice_number, client_name, total, date, status FROM invoices"
    )
    invoices = cursor.fetchall()

    # Total revenue (all invoices)
    cursor.execute("SELECT SUM(total) FROM invoices")
    total_revenue = cursor.fetchone()[0] or 0

    # Total paid
    cursor.execute("SELECT SUM(total) FROM invoices WHERE status = 'Paid'")
    total_paid = cursor.fetchone()[0] or 0

    # Total unpaid
    cursor.execute("SELECT SUM(total) FROM invoices WHERE status = 'Unpaid'")
    total_unpaid = cursor.fetchone()[0] or 0

    # Count invoices
    total_invoices = len(invoices)

    conn.close()

    return render_template(
        "tracker.html",
        invoices=invoices,
        total_revenue=total_revenue,
        total_paid=total_paid,
        total_unpaid=total_unpaid,
        total_invoices=total_invoices,
    )


@app.route("/mark-paid/<int:invoice_id>")
def mark_paid(invoice_id):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE invoices SET status = 'Paid' WHERE id = ?", (invoice_id,))
    conn.commit()
    conn.close()
    return redirect("/tracker")

@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if not session.get("inventory_access"):
        return redirect("/inventory-login")
    
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, price FROM products")
    products = cursor.fetchall()
    
    # Get quantity sold for each product from invoices
    cursor.execute('''
        SELECT description, SUM(quantity) 
        FROM items 
        GROUP BY description
    ''')
    sold_data = dict(cursor.fetchall())
    
    conn.close()
    return render_template("inventory.html", products=products, sold_data=sold_data)

@app.route("/inventory-login", methods=["GET", "POST"])
def inventory_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if password == INVENTORY_PASSWORD:
            session["inventory_access"] = True
            return redirect("/inventory")
        else:
            error = "Wrong password! Try again."
    return render_template("inventory_login.html", error=error)

@app.route("/inventory-logout")
def inventory_logout():
    session.pop("inventory_access", None)
    return redirect("/inventory-login")

@app.route("/add-product", methods=["POST"])
def add_product():
    data = request.get_json()
    name = data["name"]
    quantity = int(data["quantity"])
    price = float(data["price"])
    
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)",
                   (name, quantity, price))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/delete-product/<int:product_id>")
def delete_product(product_id):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return redirect("/inventory")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin_access"):
        return redirect("/admin-login")
    
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM invoices")
    invoices = cursor.fetchall()
    
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    
    conn.close()
    return render_template("admin.html", invoices=invoices, items=items, products=products)

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin_access"] = True
            return redirect("/admin")
        else:
            error = "Wrong password! Try again."
    return render_template("admin_login.html", error=error)

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_access", None)
    return redirect("/admin-login")


if __name__ == "__main__":
    app.run(debug=True)
