import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from dotenv import load_dotenv
from auth import auth
import pandas as pd
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
print(app.url_map)
app.secret_key = 'supersecretkey'  # Needed for session management
app.register_blueprint(auth)

# Get connection securely using env variables
def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
        ssl_ca="aiven-ca.pem"
    )

# Home page - View all products
@app.route('/')
def index():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, price, category, threshold, expiry FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/search', methods=['GET'])
def search():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))

    keyword = request.args.get('query', '')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, quantity, price, category, threshold, expiry
        FROM products
        WHERE name LIKE %s OR category LIKE %s
    """, (f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=results, search_term=keyword)

# Add Product
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        category = request.form['category']
        threshold = int(request.form['threshold'])
        expiry_date = request.form['expiry_date'] or None

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
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))

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
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE quantity < threshold")
    low_stock_products = cursor.fetchall()
    conn.close()
    return render_template('low_stock.html', products=low_stock_products)

# Delete Product
@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

from werkzeug.utils import secure_filename
import pandas as pd

# Allowed extensions
ALLOWED_EXTENSIONS = {'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/import', methods=['GET', 'POST'])
def import_excel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            df = pd.read_excel(file)

            conn = get_connection()
            cursor = conn.cursor()

            for index, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO products (name, quantity, price, category, threshold, expiry)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    row['name'], row['quantity'], row['price'],
                    row['category'], row['threshold'], row.get('expiry', None)
                ))

            conn.commit()
            conn.close()
            flash('Products imported successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid file. Please upload an Excel (.xlsx) file.', 'danger')

    return render_template('import.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
