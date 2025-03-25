# app/routes.py

from flask import Blueprint, render_template
# from .db import db

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("home.html")
