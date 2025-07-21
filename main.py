from fastapi import FastAPI, Query, Path
from models import Product, OrderDetail
from database import products, orders
from typing import Optional
from bson import ObjectId
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "Welcome to the E-commerce API!"}

@app.post("/products", status_code=HTTP_201_CREATED)
def create_product(product: Product):
    product_dict = product.dict()
    result = products.insert_one(product_dict)
    return {"id": str(result.inserted_id)}

@app.get("/products", status_code=HTTP_200_OK)
def list_products(
    name: Optional[str] = None,
    size: Optional[str] = None,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if size:
        query["sizes.size"] = size

    result = products.find(query).skip(offset).limit(limit)
    data = [{"id": str(prod["_id"]), "name": prod["name"], "price": prod["price"]} for prod in result]

    return {
        "data": data,
        "page": {
            "next": offset + limit,
            "limit": limit,
            "previous": max(offset - limit, 0)
        }
    }

@app.post("/orders", status_code=HTTP_201_CREATED)
def create_order(order: OrderDetail):
    order_dict = order.dict()
    result = orders.insert_one(order_dict)
    return {"id": str(result.inserted_id)}

@app.get("/orders/{user_id}", status_code=HTTP_200_OK)
def list_orders(
    user_id: str = Path(...),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    query = {"user_id": user_id}
    result = orders.find(query).skip(offset).limit(limit)

    order_list = []

    for order in result:
        item_details = []
        total = 0
        for item in order["items"]:
            prod = products.find_one({"_id": ObjectId(item["product_id"])})
            if prod:
                item_details.append({
                    "productDetails": {
                        "name": prod["name"],
                        "id": str(prod["_id"])
                    },
                    "qty": item["quantity"]
                })
                total += prod["price"] * item["quantity"]

        order_list.append({
            "id": str(order["_id"]),
            "items": item_details,
            "total": total
        })

    return {
        "data": order_list,
        "page": {
            "next": offset + limit,
            "limit": limit,
            "previous": max(offset - limit, 0)
        }
    }
