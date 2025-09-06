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
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                mimetype="application/json",
                status_code=405
            )

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


# --- CRUD Functions --- #

def create_product(req):
    try:
        product = req.get_json()
    except Exception:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            mimetype="application/json",
            status_code=400
        )

    if "id" not in product or "Category" not in product:
        return func.HttpResponse(
            json.dumps({"error": "ID and Category are required!"}),
            mimetype="application/json",
            status_code=400
        )

    # Ensure keys match frontend
    new_product = {
        "id": product["id"],
        "name": product.get("name", ""),
        "Category": product["Category"],
        "price": product.get("price", 0)
    }

    try:
        container.create_item(body=new_product)
        return func.HttpResponse(
            json.dumps({"message": f"Product {new_product['id']} created successfully!"}),
            mimetype="application/json",
            status_code=201
        )
    except exceptions.CosmosResourceExistsError:
        return func.HttpResponse(
            json.dumps({"error": f"Product {new_product['id']} already exists!"}),
            mimetype="application/json",
            status_code=409
        )


def read_product(req):
    product_id = req.params.get('id')
    category = req.params.get('Category')

    try:
        if product_id and category:
            # Read single item by id + partition key
            item = container.read_item(item=product_id, partition_key=category)
            return func.HttpResponse(
                json.dumps(item),
                mimetype="application/json",
                status_code=200
            )
        else:
            # Return all items (cross-partition query enabled)
            query = "SELECT * FROM c"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            return func.HttpResponse(
                json.dumps(items),
                mimetype="application/json",
                status_code=200
            )
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse(
            json.dumps({"error": "Product not found"}),
            mimetype="application/json",
            status_code=404
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


def update_product(req):
    try:
        product = req.get_json()
    except Exception:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            mimetype="application/json",
            status_code=400
        )

    if "id" not in product or "Category" not in product:
        return func.HttpResponse(
            json.dumps({"error": "ID and Category are required!"}),
            mimetype="application/json",
            status_code=400
        )

    updated_product = {
        "id": product["id"],
        "Category": product["Category"],
        "name": product.get("name", ""),
        "price": product.get("price", 0)
    }

    try:
        container.upsert_item(updated_product)
        return func.HttpResponse(
            json.dumps({"message": f"Product {updated_product['id']} updated successfully!"}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


def delete_product(req):
    product_id = req.params.get('id')
    category = req.params.get('Category')

    if not product_id or not category:
        return func.HttpResponse(
            json.dumps({"error": "ID and Category are required!"}),
            mimetype="application/json",
            status_code=400
        )

    try:
        container.delete_item(item=product_id, partition_key=category)
        return func.HttpResponse(
            json.dumps({"message": f"Product {product_id} deleted successfully!"}),
            mimetype="application/json",
            status_code=200
        )
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse(
            json.dumps({"error": "Product not found"}),
            mimetype="application/json",
            status_code=404
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )



