from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # importing the db object from __init__.py
import pandas as pd

main = Blueprint('main', __name__)

# Home Page
@main.route('/')
def home():
    return render_template('home.html')


# Register Route
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('main.register'))

        # Hashing the password before saving to the database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        # Check if username already exists
        existing_user = db.users.find_one({"username": username})
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('main.register'))

        # Saving user to the database
        db.users.insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": username,
            "password": hashed_password
        })

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch the user from the database
        user = db.users.find_one({"username": username})

        if user and check_password_hash(user['password'], password):
            # Store the user in session (to track if the user is logged in)
            session['user'] = username  # This will help us track the logged-in user
            return redirect(url_for('main.dashboard'))  # Redirecting to the dashboard page
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('main.login'))

    return render_template('login.html')


@main.route('/api/keywords')
def get_keywords():
    job_data = list(db.jobs.find({}, {"keywords": 1, "_id": 0}))
    
    keywords_list = []
    for job in job_data:
        if 'keywords' in job and isinstance(job['keywords'], str):
            keywords = job['keywords'].split(",")
            cleaned_keywords = []
            for keyword in keywords:
                cleaned_keyword = keyword.strip().lower().replace("'", "").replace("[", "").replace("]", "")
                if cleaned_keyword:
                    cleaned_keywords.append(cleaned_keyword)
            keywords_list.extend(cleaned_keywords)
    
    if len(keywords_list) == 0:
        return jsonify({"labels": [], "values": []})  # Return empty if no data found
    
    keyword_counts = pd.Series(keywords_list).value_counts().head(15)
    data = {
        "labels": keyword_counts.index.tolist(),
        "values": keyword_counts.values.tolist()
    }
    return jsonify(data)

@main.route('/api/job_titles')
def get_job_titles():
    # Fetch all job entries from the database
    job_data = list(db.jobs.find({}, {"title": 1, "_id": 0}))

    if not job_data:
        print("❌ No job title data found in the database.")
        return jsonify({"labels": [], "values": []})

    # Extract all job titles into a single list
    job_titles = [job['title'] for job in job_data if 'title' in job]

    if len(job_titles) == 0:
        print("❌ No job titles found in the dataset.")
        return jsonify({"labels": [], "values": []})

    # Count occurrences of each job title
    job_title_counts = pd.Series(job_titles).value_counts().head(20)  # Top 20 Job Titles

    # Prepare data for frontend
    data = {
        "labels": job_title_counts.index.tolist(),
        "values": job_title_counts.values.tolist()
    }

    print("✅ Job title data fetched successfully:", data)  # Debug log
    return jsonify(data)



# Dashboard Route
@main.route('/dashboard')
def dashboard():
    if 'user' not in session:  # Check if the user is logged in
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('main.login'))
    return render_template('dashboard.html')

# Logout Route
@main.route('/logout')
def logout():
    # Remove the user from the session if it exists
    session.pop('user', None)
    return redirect(url_for('main.login'))