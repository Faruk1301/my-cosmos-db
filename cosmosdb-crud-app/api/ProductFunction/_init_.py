import logging
import azure.functions as func
import os
import json
from azure.cosmos import CosmosClient, exceptions

# --- Cosmos DB config from Static Web App settings ---
COSMOS_URL = os.environ["COSMOS_URL"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
CONTAINER_NAME = os.environ["COSMOS_CONTAINER_NAME"]

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

        # --- GET all or single product ---
        if method == "GET":
            if product_id and category:
                try:
                    item = container.read_item(item=product_id, partition_key=category)
                    return func.HttpResponse(json.dumps(item), mimetype="application/json")
                except exceptions.CosmosResourceNotFoundError:
                    return func.HttpResponse(
                        json.dumps({"error": "Product not found"}),
                        status_code=404,
                        mimetype="application/json"
                    )
            else:
                query = "SELECT * FROM c"
                items = list(container.query_items(query=query, enable_cross_partition_query=True))
                return func.HttpResponse(json.dumps(items), mimetype="application/json")

        # --- POST: create product ---
        elif method == "POST":
            data = req.get_json()
            if "Category" not in data:
                return func.HttpResponse(
                    json.dumps({"error": "Missing 'Category' in request body"}),
                    status_code=400,
                    mimetype="application/json"
                )
            container.create_item(body=data)
            return func.HttpResponse(
                json.dumps({"message": "Insert done ✅", "product": data}),
                status_code=201,
                mimetype="application/json"
            )

        # --- PUT: update product ---
        elif method == "PUT":
            data = req.get_json()
            if "id" not in data or "Category" not in data:
                return func.HttpResponse(
                    json.dumps({"error": "Missing 'id' or 'Category' in request body"}),
                    status_code=400,
                    mimetype="application/json"
                )
            container.upsert_item(body=data)
            return func.HttpResponse(
                json.dumps({"message": "Update done ✅", "product": data}),
                status_code=200,
                mimetype="application/json"
            )

        # --- DELETE: remove product ---
        elif method == "DELETE":
            if not product_id or not category:
                return func.HttpResponse(
                    json.dumps({"error": "Missing 'id' or 'Category' in query params"}),
                    status_code=400,
                    mimetype="application/json"
                )
            container.delete_item(item=product_id, partition_key=category)
            return func.HttpResponse(
                json.dumps({"message": "Delete done ✅", "id": product_id, "Category": category}),
                status_code=200,
                mimetype="application/json"
            )

        else:
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


