import pandas as pd
from pymongo import MongoClient

# Load your CSV file into a DataFrame
file_path = 'app/JD-data-updated-1500.csv'  # Make sure this path is correct
df = pd.read_csv(file_path)

# Connect to your MongoDB Atlas
client = MongoClient("mongodb+srv://basuthkernikhilaws:Highway1234@cluster0.z6c3k.mongodb.net/?retryWrites=true&w=majority")
db = client["employee_portal"]
collection = db["jobs"]

# Clear existing collection (Optional - Only if you want to replace old data)
collection.delete_many({})

# Convert DataFrame to a list of dictionaries
data = df.to_dict(orient="records")

# Insert data into MongoDB
try:
    collection.insert_many(data)
    print("✅ Data imported successfully!")
except Exception as e:
    print(f"❌ Failed to import data: {e}")
