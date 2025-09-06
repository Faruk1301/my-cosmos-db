import logging
import azure.functions as func
import json
import os
from azure.cosmos import CosmosClient, exceptions

# --- Cosmos DB config from Function App settings ---
URL = os.environ["COSMOS_URL"]
KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
CONTAINER_NAME = "Products"  # Hardcoded container name

client = CosmosClient(URL, credential=KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        method = req.method
        logging.info(f"HTTP method: {method}")

        if method == "POST":
            return create_product(req)
        elif method == "GET":
            return read_product(req)
        elif method == "PUT":
            return update_product(req)
        elif method == "DELETE":
            return delete_product(req)
        else:
            return func.HttpResponse("Method not allowed", status_code=405)

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

# --- CRUD Functions ---

def create_product(req):
    product = req.get_json()
    if "id" not in product or "Category" not in product:
        return func.HttpResponse(json.dumps({"error": "ID and Category are required!"}), mimetype="application/json", status_code=400)
    try:
        container.create_item(body=product)
        return func.HttpResponse(json.dumps({"message": f"Product {product['id']} created successfully!"}), mimetype="application/json", status_code=201)
    except exceptions.CosmosResourceExistsError:
        return func.HttpResponse(json.dumps({"error": f"Product {product['id']} already exists!"}), mimetype="application/json", status_code=409)

def read_product(req):
    product_id = req.params.get('id')
    category = req.params.get('Category')

    try:
        if product_id and category:
            # Read single item
            item = container.read_item(item=product_id, partition_key=category)
            return func.HttpResponse(json.dumps(item), mimetype="application/json")
        else:
            # Return all items (cross-partition enabled)
            query = "SELECT * FROM c"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            return func.HttpResponse(json.dumps(items), mimetype="application/json")
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse(json.dumps({"error": "Product not found"}), mimetype="application/json", status_code=404)

def update_product(req):
    product = req.get_json()
    if "id" not in product or "Category" not in product:
        return func.HttpResponse(json.dumps({"error": "ID and Category are required!"}), mimetype="application/json", status_code=400)

    # Only allow keys that frontend uses
    updated_product = {
        "id": product["id"],
        "Category": product["Category"],
        "name": product.get("name", ""),
        "price": product.get("price", 0)
    }

    container.upsert_item(updated_product)
    return func.HttpResponse(json.dumps({"message": f"Product {updated_product['id']} updated successfully!"}), mimetype="application/json")

def delete_product(req):
    product_id = req.params.get('id')
    category = req.params.get('Category')

    if not product_id or not category:
        return func.HttpResponse(json.dumps({"error": "ID and Category are required!"}), mimetype="application/json", status_code=400)

    try:
        container.delete_item(item=product_id, partition_key=category)
        return func.HttpResponse(json.dumps({"message": f"Product {product_id} deleted successfully!"}), mimetype="application/json")
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse(json.dumps({"error": "Product not found"}), mimetype="application/json", status_code=404)

