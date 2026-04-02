from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
import requests

# MongoDB connection
MONGO_URI = "mongodb+srv://ameeshbains:admin1234@inventory-cluster.ibmyjvg.mongodb.net/?appName=inventory-cluster"
client = MongoClient(MONGO_URI)
db = client["inventoryDB"]
collection = db["products"]

app = FastAPI()

# ---- Pydantic model for adding a new product ----
class Product(BaseModel):
    ProductID: int
    Name: str
    UnitPrice: float
    StockQuantity: int
    Description: str


#Get Single Product
@app.get("/getSingleProduct/{product_id}")
def get_single_product(product_id: int):
    product = collection.find_one({"ProductID": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


#Get All Products
@app.get("/getAll")
def get_all():
    products = list(collection.find({}, {"_id": 0}))
    return products


#Add New Product
@app.post("/addNew")
def add_new(product: Product):
    existing = collection.find_one({"ProductID": product.ProductID})
    if existing:
        raise HTTPException(status_code=400, detail="Product ID already exists")
    collection.insert_one(product.dict())
    return {"message": "Product added successfully!"}


#Delete One Product
@app.delete("/deleteOne/{product_id}")
def delete_one(product_id: int):
    result = collection.delete_one({"ProductID": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Product {product_id} deleted successfully!"}


#Starts With
@app.get("/startsWith/{letter}")
def starts_with(letter: str):
    products = list(collection.find(
        {"Name": {"$regex": f"^{letter}", "$options": "i"}},
        {"_id": 0}
    ))
    return products


#Paginate
@app.get("/paginate")
def paginate(start: int, end: int):
    products = list(collection.find(
        {"ProductID": {"$gte": start, "$lte": end}},
        {"_id": 0}
    ).limit(10))
    return products


#Convert Price to EUR
@app.get("/convert/{product_id}")
def convert(product_id: int):
    product = collection.find_one({"ProductID": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get live exchange rate
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    rate = response.json()["rates"]["EUR"]
    
    price_eur = round(product["UnitPrice"] * rate, 2)
    return {
        "ProductID": product_id,
        "Name": product["Name"],
        "PriceUSD": product["UnitPrice"],
        "PriceEUR": price_eur,
        "ExchangeRate": rate
    }