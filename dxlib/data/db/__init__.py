from pymongo import MongoClient

# Set up the MongoDB connection
client = MongoClient("mongodb://localhost:27017/")

# Access a specific database
db = client["your_database_name"]

# Access a specific collection within the database
collection = db["your_collection_name"]

# Perform database operations
# Example: Insert a document into the collection
document = {"name": "John Doe", "email": "johndoe@example.com", "age": 30}
result = collection.insert_one(document)
print("Inserted document ID:", result.inserted_id)

# Close the MongoDB connection
client.close()
