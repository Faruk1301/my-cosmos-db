import logging
import azure.functions as func
import os
import json
from azure.cosmos import CosmosClient, exceptions

# --- Cosmos DB config from Function App settings ---
COSMOS_URL = os.environ["COSMOS_URL"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
CONTAINER_NAME = "Products"  # Hardcoded container name

# --- Initialize Cosmos client ---
client = CosmosClient(COSMOS_URL, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function processed a request.')

    try:
        method = req.method
        product_id = req.params.get('id')
        category = req.params.get('Category')
        
        if method == "GET":
            if product_id and category:
                # Get single product by id + category (partition key)
                try:
                    item = container.read_item(item=product_id, partition_key=category)
                    return func.HttpResponse(json.dumps(item), mimetype="application/json")
                except exceptions.CosmosResourceNotFoundError:
                    return func.HttpResponse("Product not found.", status_code=404)
            else:
                # Return all products
                query = "SELECT * FROM c"
                items = list(container.query_items(query=query, enable_cross_partition_query=True))
                return func.HttpResponse(json.dumps(items), mimetype="application/json")

        elif method == "POST":
            data = req.get_json()
            if "Category" not in data:
                return func.HttpResponse("Missing 'Category' in request body.", status_code=400)
            container.create_item(body=data)
            return func.HttpResponse("Product created successfully.", status_code=201)

        elif method == "PUT":
            data = req.get_json()
            if "id" not in data or "Category" not in data:
                return func.HttpResponse("Missing 'id' or 'Category' in request body.", status_code=400)
            container.upsert_item(body=data)
            return func.HttpResponse("Product updated successfully.", status_code=200)

        elif method == "DELETE":
            if not product_id or not category:
                return func.HttpResponse("Missing 'id' or 'Category' in query params.", status_code=400)
            container.delete_item(item=product_id, partition_key=category)
            return func.HttpResponse("Product deleted successfully.", status_code=200)

        else:
            return func.HttpResponse("Method not allowed.", status_code=405)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)

