from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth = Blueprint('auth', __name__)

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Login attempt: {username} / {password}")  # Debug line

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('auth.login'))
