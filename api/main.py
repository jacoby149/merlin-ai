from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Auto Code This API",
    description="Visit localhost:3001 to code this API automatically",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

products = [
    Product(id=1, name="Laptop", description="A high performance laptop", price=999.99, stock=10),
    Product(id=2, name="Smartphone", description="A latest model smartphone", price=499.99, stock=20),
    Product(id=3, name="Headphones", description="Noise-cancelling headphones", price=199.99, stock=15),
]

@app.get("/health_check", description="Returns a health status. You can try asking the ai chat to make this endpoint return the health of the mongodb connection!")
def health_check():
    return {"Hello": "World"}

@app.get("/products", response_model=List[Product], description="Get a list of products available in the store.")
def get_products():
    return products

@app.get("/products/{product_id}", response_model=Product, description="Get a product by its ID.")
def get_product(product_id: int):
    for product in products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")