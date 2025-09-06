import logging
import azure.functions as func
import json
import os
from azure.cosmos import CosmosClient, exceptions

# Cosmos DB config from Application Settings
URL = os.environ["COSMOS_URL"]
KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
CONTAINER_NAME = "Products"

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
            return json_response({"error": "Method not allowed"}, 405)

    except Exception as e:
        logging.error(str(e))
        return json_response({"error": str(e)}, 500)


# --- Helper for consistent JSON responses ---
def json_response(data, status=200):
    return func.HttpResponse(
        json.dumps(data),
        mimetype="application/json",
        status_code=status
    )


# --- CRUD Functions --- #
def create_product(req):
    try:
        product = req.get_json()
    except Exception:
        return json_response({"error": "Invalid JSON body"}, 400)

    if "id" not in product or "Category" not in product:
        return json_response({"error": "ID and Category are required!"}, 400)

    new_product = {
        "id": product["id"],
        "name": product.get("name", ""),
        "Category": product["Category"],
        "price": product.get("price", 0)
    }

    try:
        container.create_item(body=new_product)
        return json_response({"message": f"Product {new_product['id']} created successfully!"}, 201)
    except exceptions.CosmosResourceExistsError:
        return json_response({"error": f"Product {new_product['id']} already exists!"}, 409)


def read_product(req):
    product_id = req.params.get('id')
    category = req.params.get('Category')

    try:
        if product_id and category:
            item = container.read_item(item=product_id, partition_key=category)
            return json_response(item, 200)
        else:
            query = "SELECT * FROM c"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            return json_response(items, 200)

    except exceptions.CosmosResourceNotFoundError:
        return json_response({"error": "Product not found"}, 404)
    except Exception as e:
        return json_response({"error": str(e)}, 500)


def update_product(req):
    try:
        product = req.get_json()
    except Exception:
        return json_response({"error": "Invalid JSON body"}, 400)

    if "id" not in product or "Category" not in product:
        return json_response({"error": "ID and Category are required!"}, 400)

    updated_product = {
        "id": product["id"],
        "Category": product["Category"],
        "name": product.get("name", ""),
        "price": product.get("price", 0)
    }

    try:
        container.upsert_item(updated_product)
        return json_response({"message": f"Product {updated_product['id']} updated successfully!"}, 200)
    except Exception as e:
        return json_response({"error": str(e)}, 500)


def delete_product(req):
    product_id = req.params.get('id')
    category = req.params.get('Category')

    if not product_id or not category:
        return json_response({"error": "ID and Category are required!"}, 400)

    try:
        container.delete_item(item=product_id, partition_key=category)
        return json_response({"message": f"Product {product_id} deleted successfully!"}, 200)
    except exceptions.CosmosResourceNotFoundError:
        return json_response({"error": "Product not found"}, 404)
    except Exception as e:
        return json_response({"error": str(e)}, 500)

