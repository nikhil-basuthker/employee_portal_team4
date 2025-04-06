from flask import Flask
from flask_pymongo import PyMongo
import os

mongo = None
db = None

def create_app():
    app = Flask(__name__)
    
    app.config["SECRET_KEY"] = "nikhil1005"
    app.config["MONGO_URI"] = "mongodb+srv://basuthkernikhilaws:Highway1234@cluster0.z6c3k.mongodb.net/employee_portal?retryWrites=true&w=majority&authSource=admin"
    
    global mongo, db
    mongo = PyMongo(app)
    db = mongo.db  # This connects to your `employee_portal` database
    
    try:
        # Check if the connection is successful
        mongo.cx.server_info()
        print("✅ Connected successfully to MongoDB!")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")

    from .routes import main
    app.register_blueprint(main)

    return app
