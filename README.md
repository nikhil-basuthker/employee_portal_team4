
# Cloud JobLens

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

A Flask-powered Cloud JobLens Platform focused on cloud job trends, skills, and personalized career insights.

## Project Description

Cloud JobLens is a data-driven web application designed to help students and professionals explore real-time AWS job market trends. Users can upload their resumes to get tailored skill recommendations, access dashboards on in-demand AWS skills, and gain salary and job insights to make smarter career decisions.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Installation

1. Clone the repository:
```
git clone https://github.com/nikhil-basuthker/employee_portal_team4.git
cd employee_portal_team4
```

2. Create and activate a virtual environment:
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run the application:
```
flask run --host=0.0.0.0 --port=5000
```

## Usage

Once the server is running, access the app at:

```
http://localhost:5000
```

User Flow:
- Register/Login
- Upload a resume (PDF or DOCX)
- View extracted AWS skills
- Analyze job/salary trends on dashboard

## Features

- User Registration & Login (MongoDB)
- Resume Upload and AWS Skill Extraction
- Interactive Dashboards using Chart.js or Plotly.js
- Career Suggestions and Job Market Analytics
- MongoDB-powered skill tracking

## Project Structure

```
employee_portal_team4/
├── app/
│   ├── static/
│   │   ├── css/style.css
│   │   └── images/
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── navbarloggedin.html
│   │   └── navbarloggedout.html
│   ├── __init__.py
│   └── routes.py
├── main.py
├── requirements.txt
└── README.md
```

## Contributing

To contribute to this project:

1. Fork the repository to your GitHub account.
2. Clone your forked repository:
```
git clone https://github.com/yourusername/employee_portal_team4.git
```
3. Create a new branch for your changes:
```
git checkout -b your-feature-branch
```
4. Make your changes and commit:
```
git add .
git commit -m "Add your message here"
```
5. Push to your forked repository:
```
git push origin your-feature-branch
```
6. Create a pull request from your branch to the `main` branch of the original repository.

Team members should coordinate with each other and ensure no conflicts before merging.

## License

This project is licensed under the MIT License.

## Acknowledgements

- Flask - Python Web Framework
- Bootstrap - Frontend Styling
- MongoDB Atlas - NoSQL Database
- Chart.js / Plotly.js - Interactive Graphs and Dashboards
- Resume Parser Tools
