from flask import Flask, request, redirect, render_template,psycopg2,os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse

# Read database URL from environment variable (set by Render)
DATABASE_URL = os.environ.get("DATABASE_URL")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

# Combine GET and POST into one function for /submit-signup
@app.route('/submit-signup', methods=['GET', 'POST'])
def submit_signup():
    if request.method == 'GET':
        # Redirect to signup page if user visits submit URL directly via GET
        return redirect('/signup')

    # POST: process form submission
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    username = request.form.get('username')
    raw_password = request.form.get('password')

    if not fullname or not email or not username or not raw_password:
        return "Please fill all fields", 400

    hashed_password = generate_password_hash(raw_password)

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (fullname, email, username, password)
        VALUES (?, ?, ?, ?)
    ''', (fullname, email, username, hashed_password))
    conn.commit()
    conn.close()

    return render_template('signup_success.html', fullname=fullname, email=email, username=username)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/submit-login', methods=['POST'])
def submit_login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return "Please enter email and password", 400

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password, fullname FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user:
        hashed_password, fullname = user
        if check_password_hash(hashed_password, password):
            return f"✅ Welcome back, {fullname}!"
        else:
            return "❌ Incorrect password!"
    else:
        return "❌ Email not found!"

@app.route('/all_users')
def all_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT fullname, email, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('all_users.html', users=users)
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
