import pandas as pd
from pymongo import MongoClient

# Load your CSV file into a DataFrame
# file_path = 'app/JD-data-updated-1500.csv'  # Make sure this path is correct
# df = pd.read_csv(file_path)

# Connect to your MongoDB Atlas
client = MongoClient("mongodb+srv://basuthkernikhilaws:Highway1234@cluster0.z6c3k.mongodb.net/?retryWrites=true&w=majority")
db = client["employee_portal"]
collection = db["jobs"]

# Step 1: Drop existing data
collection.drop()
print("✅ Existing 'jobs' collection dropped.")

# Step 2: Load new dataset
df = pd.read_csv("app/dataset/cloud_jobs_dataset.csv")

# Optional: Clean column names (strip whitespace, lowercase)
df.columns = [col.strip().lower() for col in df.columns]

# Optional: Convert to dictionary and drop any rows with missing job title/location
records = df.dropna(subset=["job_title", "location"]).to_dict(orient="records")

# Step 3: Insert into MongoDB
collection.insert_many(records)
print(f"✅ {len(records)} new job records inserted successfully!")

