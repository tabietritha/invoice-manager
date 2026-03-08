from flask import Flask, redirect, render_template, request
import sqlite3


def save_invoice(invoice_number, client_name, total, invoice_date, items, status):
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
    for item in items:
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

    conn.commit()
    conn.close()


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


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
    status = request.form.get("status", "Unpaid")  # Default to 'Unpaid' if not provided

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
    save_invoice(invoice_number, client_name, total, invoice_date, items, status)

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


if __name__ == "__main__":
    app.run(debug=True)
