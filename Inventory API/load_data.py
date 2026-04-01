import csv
import json
from pymongo import MongoClient

# Paste your MongoDB connection string here
MONGO_URI = "mongodb+srv://ameeshbains:admin1234@inventory-cluster.ibmyjvg.mongodb.net/?appName=inventory-cluster"
DB_NAME = "inventoryDB"
COLLECTION_NAME = "products"

def load_csv_to_mongo(filepath):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Clear existing data so we don't duplicate on re-runs
    collection.drop()

    products = []

    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product = {
                "ProductID": int(row["ProductID"]),
                "Name": row["Name"],
                "UnitPrice": float(row["UnitPrice"]),
                "StockQuantity": int(row["StockQuantity"]),
                "Description": row["Description"]
            }
            products.append(product)

    collection.insert_many(products)
    print(f" Loaded {len(products)} products into MongoDB!")
    client.close()

if __name__ == "__main__":
    load_csv_to_mongo("products.csv")