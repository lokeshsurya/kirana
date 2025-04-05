import mysql.connector
from datetime import datetime


# ---------------------- DB Connection ----------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="kirana",                 # change if using a different user
        password="kiranapass",  # 🔐 replace with your MySQL password
        database="kirana_inventory"
    )

# ---------------------- Add Product ----------------------
def add_product():
    name = input("Enter product name: ")
    quantity = int(input("Enter quantity: "))
    price = float(input("Enter price: "))
    category = input("Enter category: ")
    threshold = int(input("Enter low stock threshold: "))
    expiry_date = input("Enter expiry date (YYYY-MM-DD): ")

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO products (name, quantity, price, category, threshold, expiry_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (name, quantity, price, category, threshold, expiry_date)

    cursor.execute(query, values)
    conn.commit()
    conn.close()

    print("✅ Product added successfully!")


# ---------------------- View All Products ----------------------
def view_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, quantity, price, category, threshold, expiry_date FROM products")


    rows = cursor.fetchall()

    print("\n📦 Inventory List:")
    print("-" * 100)
    print(f"{'ID':<5} {'Name':<15} {'Qty':<6} {'Price':<8} {'Category':<12} {'Thresh':<8} {'Expiry':<12}")
    print("-" * 100)

    for row in rows:
        product_id, name, quantity, price, category, threshold, expiry_date = row
        expiry_str = expiry_date.strftime("%Y-%m-%d") if expiry_date else "N/A"
        print(f"{product_id:<5} {name:<15} {quantity:<6} {price:<8} {category:<12} {threshold:<8} {expiry_str:<12}")

    conn.close()


# ---------------------- Menu ----------------------
def menu():
    print("\n--- Kirana Store Inventory ---")
    print("1. Add Product")
    print("2. View Products")
    print("3. Exit")
    print("5. Update Expiry Date")
    print("6. Exit")

# ---------------------- Low Stock alert ----------------------
def check_low_stock():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, threshold FROM products")
    results = cursor.fetchall()
    conn.close()

    print("\n🚨 Low Stock Alerts:")
    print("-" * 50)
    has_alerts = False
    for product_id, name, quantity, threshold in results:
        if quantity <= threshold:
            has_alerts = True
            print(f"⚠️  {name} (ID: {product_id}) is low on stock. Qty: {quantity}, Threshold: {threshold}")

    if not has_alerts:
        print("✅ All products are sufficiently stocked.")

# ---------------------- Update Expiry Date ----------------------
def update_expiry_date():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        product_id = int(input("Enter Product ID to update expiry date: "))
        new_expiry = input("Enter new expiry date (YYYY-MM-DD): ")
        new_expiry_date = datetime.strptime(new_expiry, "%Y-%m-%d").date()

        cursor.execute("UPDATE products SET expiry_date = %s WHERE id = %s", (new_expiry_date, product_id))
        conn.commit()
        print("✅ Expiry date updated successfully!")

    except ValueError:
        print("❌ Invalid input. Please enter the date in YYYY-MM-DD format.")
    except Exception as e:
        print("❌ Error:", e)

    cursor.close()
    conn.close()

# ---------------------- Main Loop ----------------------
while True:
    print("\n📋 Kirana Inventory System")
    print("1. Add Product")
    print("2. View Products")
    print("3. Check Low Stock Alerts")
    print("4. Update Expiry Date")
    print("5. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        add_product()
    elif choice == "2":
        view_products()
    elif choice == "3":
        check_low_stock()
    elif choice == "4":
        update_expiry_date()
    elif choice == "5":
        break
    else:
        print("❌ Invalid choice. Please try again.")



