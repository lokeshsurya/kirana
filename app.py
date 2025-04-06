from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)

db = mysql.connector.connect(
    host="mysql-131cd9b3-lokeshsuryawanshi818-8948.h.aivencloud.com",
    port=10761,
    user="avnadmin",
    password="AVNS_aAUNxuEz5z632G1ZK26",
    database="defaultdb",
    ssl_ca="aiven-ca.pem"  # optional: Aiven gives a cert you can use for secure SSL
)

# Home page - View all products
@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, price, category, threshold, expiry FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Add Product
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        category = request.form['category']
        threshold = int(request.form['threshold'])
        expiry_date = request.form['expiry_date']
        expiry_date = expiry_date if expiry_date else None

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, quantity, price, category, threshold, expiry)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, quantity, price, category, threshold, expiry_date))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_product.html')

# Update Expiry Date
@app.route('/update-expiry/<int:product_id>', methods=['GET', 'POST'])
def update_expiry(product_id):
    if request.method == 'POST':
        new_date = request.form['expiry_date']
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET expiry = %s WHERE id = %s", (new_date, product_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('update_expiry.html', product_id=product_id)

# Low Stock Alert
@app.route('/low-stock')
def low_stock():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE quantity < threshold")
    low_stock_products = cursor.fetchall()
    conn.close()
    return render_template('low_stock.html', products=low_stock_products)

if __name__ == '__main__':
    app.run(debug=True)
