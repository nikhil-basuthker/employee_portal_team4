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

from collections import Counter

# Employment Type Distribution API
@main.route('/api/employment_type')
def get_employment_type_distribution():
    job_data = list(db.jobs.find({}, {"employment_type": 1, "_id": 0}))

    if not job_data:
        print("❌ No employment type data found in the database.")
        return jsonify({"labels": [], "values": []})

    employment_types = [job.get('employment_type', 'Unknown') for job in job_data]

    if len(employment_types) == 0:
        return jsonify({"labels": [], "values": []})

    employment_type_counts = pd.Series(employment_types).value_counts()
    data = {
        "labels": employment_type_counts.index.tolist(),
        "values": employment_type_counts.values.tolist()
    }

    print("✅ Employment type data fetched successfully:", data)
    return jsonify(data)


# Experience Level Analysis API
@main.route('/api/experience_level')
def get_experience_level_distribution():
    job_data = list(db.jobs.find({}, {"experience_level": 1, "_id": 0}))

    if not job_data:
        print("❌ No experience level data found in the database.")
        return jsonify({"labels": [], "values": []})

    experience_levels = [job.get('experience_level', 'Unknown') for job in job_data]

    if len(experience_levels) == 0:
        return jsonify({"labels": [], "values": []})

    experience_level_counts = pd.Series(experience_levels).value_counts()
    data = {
        "labels": experience_level_counts.index.tolist(),
        "values": experience_level_counts.values.tolist()
    }

    print("✅ Experience level data fetched successfully:", data)
    return jsonify(data)

# Location Analysis API Route
@main.route('/api/location_analysis')
def location_analysis():
    # Fetch all job entries from the database
    job_data = list(db.jobs.find({}, {"location": 1, "_id": 0}))

    if not job_data:
        return jsonify({"labels": [], "values": []})

    # Extract all locations into a single list
    locations = [job['location'] for job in job_data if 'location' in job]

    if len(locations) == 0:
        return jsonify({"labels": [], "values": []})

    # Count occurrences of each location
    location_counts = pd.Series(locations).value_counts().head(15)  # Top 15 Locations

    data = {
        "labels": location_counts.index.tolist(),
        "values": location_counts.values.tolist()
    }

    return jsonify(data)


# Salary Range Analysis API Route
@main.route('/api/salary_analysis')
def salary_analysis():
    # Fetch all job entries from the database
    job_data = list(db.jobs.find({}, {"salary_range": 1, "_id": 0}))

    if not job_data:
        return jsonify({"ranges": [], "counts": []})

    # Extract salary ranges into a single list
    salary_ranges = [job['salary_range'] for job in job_data if 'salary_range' in job and isinstance(job['salary_range'], str)]

    if len(salary_ranges) == 0:
        return jsonify({"ranges": [], "counts": []})

    # Clean salary range data (remove '$', ',', 'K', ' per year', etc.)
    cleaned_ranges = []
    for salary in salary_ranges:
        try:
            parts = salary.replace('$', '').replace(',', '').replace(' per year', '').replace('K', '000').split('-')
            if len(parts) == 2:
                low, high = int(parts[0].strip()), int(parts[1].strip())
                avg_salary = (low + high) / 2
                cleaned_ranges.append(avg_salary)
        except ValueError:
            continue

    # Create salary bins for visualization
    bins = [0, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000]
    labels = ['$0-50K', '$50K-100K', '$100K-150K', '$150K-200K', '$200K-250K', '$250K-300K', '$300K-350K', '$350K-400K']

    salary_bins = pd.cut(cleaned_ranges, bins=bins, labels=labels)
    salary_counts = salary_bins.value_counts().sort_index()

    data = {
        "ranges": salary_counts.index.tolist(),
        "counts": salary_counts.values.tolist()
    }

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