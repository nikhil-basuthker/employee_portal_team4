from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # importing the db object from __init__.py
import pandas as pd

main = Blueprint('main', __name__)

# Home Page
@main.route('/')
def home():
    return render_template('home.html')

def build_filter_query():
    query = {}
    location = request.args.get("location")
    experience = request.args.get("experience")
    remote = request.args.get("remote")
    platform = request.args.get("platform")
    job_function = request.args.get("job_function")
    job_age = request.args.get("job_age")

    if location and location != "All":
        query["location"] = location
    if experience and experience != "All":
        query["experience_level"] = experience
    if remote and remote != "All":
        query["remote_option"] = remote
    if platform and platform != "All":
        query["cloud_platform"] = platform
    if job_function and job_function != "All":
        query["job_function"] = job_function
    if job_age and job_age != "All":
        if job_age == "🟢 Fresh Postings (Last 7 Days)":
            query["how_much_older"] = {"$regex": r"^[1-7] days$"}
        elif job_age == "🟡 Active Listings (8–30 Days)":
            query["how_much_older"] = {"$regex": r"^(8|9|1[0-9]|2[0-9]|30) days$"}
        elif job_age == "🔴 Stale Listings (Over 30 Days)":
            query["how_much_older"] = "older than 30 days"


    return query

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
    search_query = request.args.get('search')

    # 🔄 Use the reusable filter builder
    query = build_filter_query()

    # Parse search terms (comma-separated)
    search_terms = []
    if search_query:
        search_terms = [term.strip().lower() for term in search_query.split(",") if term.strip()]

    # Fetch job data
    job_data = list(db.jobs.find(query, {"required_skills": 1, "_id": 0}))
    skills_list = []

    for job in job_data:
        raw_skills = job.get("required_skills", [])
        if isinstance(raw_skills, str) and raw_skills.startswith("[") and raw_skills.endswith("]"):
            cleaned = raw_skills.strip("[]").replace("'", "")
            skills = [skill.strip().lower() for skill in cleaned.split(",") if skill.strip()]

            if not search_terms:
                skills_list.extend(skills)
            else:
                matched = [s for s in skills if s in search_terms]
                if matched:
                    skills_list.extend(matched)

    if not skills_list:
        return jsonify({"labels": [], "values": []})

    skill_counts = pd.Series(skills_list).value_counts()

    data = {
        "labels": skill_counts.index.tolist(),
        "values": skill_counts.values.tolist()
    }

    return jsonify(data)


@main.route('/api/job_titles')
def get_job_titles():
    search = request.args.get('search')

    # 🔄 Use centralized filtering logic
    query = build_filter_query()

    job_data = list(db.jobs.find(query, {"job_title": 1, "required_skills": 1, "_id": 0}))

    job_titles = []
    if search:
        keywords = [kw.strip().lower() for kw in search.split(",") if kw.strip()]
        for job in job_data:
            raw_skills = job.get("required_skills", [])
            if isinstance(raw_skills, str) and raw_skills.startswith("[") and raw_skills.endswith("]"):
                cleaned = raw_skills.strip("[]").replace("'", "")
                skill_list = [s.strip().lower() for s in cleaned.split(",") if s.strip()]
                if any(kw in skill_list for kw in keywords):
                    job_title = job.get('job_title')
                    if job_title:
                        job_titles.append(job_title)
    else:
        job_titles = [job['job_title'] for job in job_data if 'job_title' in job and isinstance(job['job_title'], str)]

    if not job_titles:
        return jsonify({"labels": [], "values": []})

    job_title_counts = pd.Series(job_titles).value_counts().head(20)

    return jsonify({
        "labels": job_title_counts.index.tolist(),
        "values": job_title_counts.values.tolist()
    })


from collections import Counter

# Employment Type Distribution API
@main.route('/api/employment_type')
def get_employment_type_distribution():
    search_keywords = request.args.get('search')

    # ✅ Use centralized filtering logic
    query = build_filter_query()

    job_data = list(db.jobs.find(query, {"employment_type": 1, "required_skills": 1, "_id": 0}))

    if search_keywords:
        keywords = [k.strip().lower() for k in search_keywords.split(",") if k.strip()]
        filtered_jobs = []
        for job in job_data:
            raw_skills = job.get("required_skills", [])
            if isinstance(raw_skills, str) and raw_skills.startswith("[") and raw_skills.endswith("]"):
                skill_list = [s.strip().lower().replace("'", "") for s in raw_skills.strip("[]").split(",")]
                if any(keyword in skill_list for keyword in keywords):
                    filtered_jobs.append(job)
        job_data = filtered_jobs

    employment_types = [job.get('employment_type', 'Unknown') for job in job_data]

    if not employment_types:
        return jsonify({"labels": [], "values": []})

    employment_type_counts = pd.Series(employment_types).value_counts()

    return jsonify({
        "labels": employment_type_counts.index.tolist(),
        "values": employment_type_counts.values.tolist()
    })



@main.route('/api/experience_level')
def get_experience_level_distribution():
    search_keywords = request.args.get('search')

    # ✅ Use the centralized filtering logic
    query = build_filter_query()

    job_data = list(db.jobs.find(query, {"experience_level": 1, "required_skills": 1, "_id": 0}))

    age = request.args.get("job_age")
    if age and age != "All":
        query["how_much_older"] = age

    if search_keywords:
        keywords = [k.strip().lower() for k in search_keywords.split(",") if k.strip()]
        filtered_jobs = []
        for job in job_data:
            raw_skills = job.get("required_skills", [])
            if isinstance(raw_skills, str) and raw_skills.startswith("[") and raw_skills.endswith("]"):
                skill_list = [s.strip().lower().replace("'", "") for s in raw_skills.strip("[]").split(",")]
                if any(keyword in skill_list for keyword in keywords):
                    filtered_jobs.append(job)
        job_data = filtered_jobs

    experience_levels = [job.get('experience_level', 'Unknown') for job in job_data]

    if not experience_levels:
        return jsonify({"labels": [], "values": []})

    experience_level_counts = pd.Series(experience_levels).value_counts()

    return jsonify({
        "labels": experience_level_counts.index.tolist(),
        "values": experience_level_counts.values.tolist()
    })


@main.route('/api/experience_levels')
def get_unique_experience_levels():
    # Get distinct values from the 'experience_level' field
    raw_levels = db.jobs.distinct("experience_level")

    # Clean and filter valid strings
    cleaned_levels = sorted([
        level for level in raw_levels
        if isinstance(level, str) and level.strip()
    ])

    return jsonify(cleaned_levels)


# Location Analysis API Route
import re

@main.route('/api/location_analysis')
def location_analysis():
    # ✅ Use centralized filter query
    query = build_filter_query()

    job_data = list(db.jobs.find(query, {"location": 1, "_id": 0}))

    state_counts = {}

    for job in job_data:
        location_str = job.get("location", "")
        match = re.search(r',\s*([A-Z]{2})$', location_str)
        if match:
            state = match.group(1)
            state_counts[state] = state_counts.get(state, 0) + 1

    return jsonify({
        "states": list(state_counts.keys()),
        "counts": list(state_counts.values())
    })



# Salary Range Analysis API Route
@main.route('/api/salary_analysis')
def salary_analysis():
    search_keywords = request.args.get('search')

    # ✅ Use centralized filtering logic
    query = build_filter_query()

    job_data = list(db.jobs.find(query, {"salary_avg": 1, "required_skills": 1, "_id": 0}))

    # 🔍 Filter by keywords
    if search_keywords:
        keywords = [k.strip().lower() for k in search_keywords.split(",") if k.strip()]
        filtered_jobs = []
        for job in job_data:
            raw_skills = job.get("required_skills", "")
            if isinstance(raw_skills, str) and raw_skills.startswith("[") and raw_skills.endswith("]"):
                skill_list = [s.strip().lower().replace("'", "") for s in raw_skills.strip("[]").split(",")]
                if any(keyword in skill_list for keyword in keywords):
                    filtered_jobs.append(job)
        job_data = filtered_jobs

    # 🧮 Extract salary values
    salary_averages = []
    for job in job_data:
        raw_salary = job.get('salary_avg')
        if isinstance(raw_salary, str):
            try:
                cleaned = raw_salary.replace('$', '').replace(',', '').strip()
                salary_averages.append(float(cleaned))
            except ValueError:
                continue
        elif isinstance(raw_salary, (int, float)):
            salary_averages.append(raw_salary)

    if not salary_averages:
        return jsonify({"ranges": [], "counts": []})

    # 💰 Define salary bins
    bins = [0, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000]
    labels = ['$0-50K', '$50K-100K', '$100K-150K', '$150K-200K',
              '$200K-250K', '$250K-300K', '$300K-350K', '$350K-400K']

    salary_bins = pd.cut(salary_averages, bins=bins, labels=labels)
    salary_counts = salary_bins.value_counts().sort_index()

    return jsonify({
        "ranges": salary_counts.index.tolist(),
        "counts": salary_counts.values.tolist()
    })


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

@main.route('/api/locations')
def get_unique_locations():
    job_data = db.jobs.distinct("location")
    
    # Clean and filter non-string values before sorting
    locations = sorted([loc for loc in job_data if isinstance(loc, str) and loc.strip()])
    
    return jsonify(locations)

@main.route('/api/remote_options')
def get_unique_remote_options():
    options = db.jobs.distinct("remote_option")
    cleaned = sorted([opt for opt in options if isinstance(opt, str) and opt.strip()])
    return jsonify(cleaned)


@main.route('/api/platforms')
def get_unique_platforms():
    options = db.jobs.distinct("cloud_platform")
    cleaned = sorted([opt for opt in options if isinstance(opt, str) and opt.strip()])
    return jsonify(cleaned)


@main.route('/api/job_functions')
def get_unique_job_functions():
    options = db.jobs.distinct("job_function")
    cleaned = sorted([opt for opt in options if isinstance(opt, str) and opt.strip()])
    return jsonify(cleaned)

@main.route('/api/job_ages')
def get_unique_job_ages():
    return jsonify([
        "🟢 Fresh Postings (Last 7 Days)",
        "🟡 Active Listings (8–30 Days)",
        "🔴 Stale Listings (Over 30 Days)"
    ])

@main.route('/cloud-insights')
def cloud_insights():
    return render_template('cloud_insights.html')

import re

def build_insights_filter_query():
    query = {}
    exp = request.args.get("experience")
    age = request.args.get("job_age")

    if exp and exp != "All":
        query["experience_level"] = exp

    if age and age != "All":
        if age == "🟢 Fresh Postings (Last 7 Days)":
            query["how_much_older"] = {"$regex": r"^[1-7] days$"}
        elif age == "🟡 Active Listings (8–30 Days)":
            query["how_much_older"] = {"$regex": r"^(8|9|1[0-9]|2[0-9]|30) days$"}
        elif age == "🔴 Stale Listings (Over 30 Days)":
            query["how_much_older"] = "older than 30 days"

    return query

from collections import Counter

@main.route('/api/cloud_skills_radar')
def cloud_skills_radar():
    platforms = ["AWS", "GCP", "Azure"]
    result = []

    for platform in platforms:
        query = build_insights_filter_query()
        query["cloud_platform"] = platform
        jobs = db.jobs.find(query, {"required_skills": 1})

        skills_list = []
        for job in jobs:
            raw_skills = job.get("required_skills", "")
            if isinstance(raw_skills, str) and raw_skills.startswith("[") and raw_skills.endswith("]"):
                cleaned = raw_skills.strip("[]").replace("'", "")
                skills = [s.strip().lower() for s in cleaned.split(",") if s.strip()]
                skills_list.extend(skills)

        top_skills = Counter(skills_list).most_common(7)
        result.append({
            "platform": platform,
            "labels": [s for s, _ in top_skills],
            "values": [c for _, c in top_skills]
        })

    return jsonify(result)


from collections import Counter

@main.route('/api/cloud_platform_titles_sunburst')
def cloud_platform_titles_sunburst():
    platforms = ["AWS", "GCP", "Azure"]
    labels = []
    parents = []
    values = []

    for platform in platforms:
        query = build_insights_filter_query()
        query["cloud_platform"] = platform
        jobs = db.jobs.find(query, {"job_title": 1})

        title_counts = Counter()
        for job in jobs:
            title = job.get("job_title", "Unknown")
            if isinstance(title, str) and title.strip():
                title_counts[title.strip()] += 1

        top_titles = title_counts.most_common(5)
        labels.append(platform)
        parents.append("")
        values.append(sum(count for _, count in top_titles))

        for title, count in top_titles:
            labels.append(title)
            parents.append(platform)
            values.append(count)

    return jsonify({
        "labels": labels,
        "parents": parents,
        "values": values
    })




@main.route('/api/cloud_platform_salary_violin')
def cloud_platform_salary_violin():
    platforms = ["AWS", "GCP", "Azure"]
    result = {platform: [] for platform in platforms}

    for platform in platforms:
        query = build_insights_filter_query()
        query["cloud_platform"] = platform
        jobs = db.jobs.find(query, {"salary_avg": 1})

        for job in jobs:
            raw_salary = job.get("salary_avg")
            if isinstance(raw_salary, str):
                try:
                    cleaned = raw_salary.replace("$", "").replace(",", "").strip()
                    result[platform].append(float(cleaned))
                except:
                    continue
            elif isinstance(raw_salary, (int, float)):
                result[platform].append(raw_salary)

    return jsonify(result)



# State centroid reference for plotting
STATE_COORDS = {
    "CA": (36.7783, -119.4179), "TX": (31.9686, -99.9018), "NY": (43.0000, -75.0000),
    "FL": (27.9944, -81.7603), "WA": (47.7511, -120.7401), "IL": (40.6331, -89.3985),
    "GA": (32.1656, -82.9001), "OH": (40.4173, -82.9071), "NC": (35.7596, -79.0193),
    "VA": (37.4316, -78.6569), "MA": (42.4072, -71.3824), "PA": (41.2033, -77.1945),
    "MI": (44.3148, -85.6024), "AZ": (34.0489, -111.0937), "CO": (39.5501, -105.7821),
    "NJ": (40.0583, -74.4057), "MN": (46.7296, -94.6859), "MO": (37.9643, -91.8318),
    "IN": (40.2672, -86.1349), "WI": (43.7844, -88.7879)
}

@main.route('/api/cloud_platform_bubblemap')
def cloud_platform_bubblemap():
    platforms = ["AWS", "GCP", "Azure"]
    bubble_data = []

    for platform in platforms:
        query = build_insights_filter_query()
        query["cloud_platform"] = platform
        jobs = db.jobs.find(query, {"location": 1})
        state_counts = {}

        for job in jobs:
            loc = job.get("location", "")
            match = re.search(r",\s*([A-Z]{2})$", loc)
            if match:
                state = match.group(1)
                if state in STATE_COORDS:
                    state_counts[state] = state_counts.get(state, 0) + 1

        for state, count in state_counts.items():
            lat, lon = STATE_COORDS[state]
            bubble_data.append({
                "platform": platform,
                "state": state,
                "count": count,
                "lat": lat,
                "lon": lon
            })

    return jsonify(bubble_data)
