import logging
import azure.functions as func
import os
import json
from azure.cosmos import CosmosClient, exceptions

# --- Cosmos DB config from Function App settings ---
url = os.environ["COSMOS_URL"]
key = os.environ["COSMOS_KEY"]
database_name = os.environ["DATABASE_NAME"]
container_name = os.environ["COSMOS_CONTAINER_NAME"]

client = CosmosClient(url, credential=key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Request method: %s", req.method)

    try:
        # Insert / Update
        if req.method in ["POST", "PUT"]:
            try:
                data = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON"}),
                    status_code=400,
                    mimetype="application/json"
                )

            # Required field check
            required_fields = ["id", "name", "Category", "price"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                return func.HttpResponse(
                    json.dumps({"error": f"Missing fields: {', '.join(missing)}"}),
                    status_code=400,
                    mimetype="application/json"
                )

            if req.method == "POST":
                container.create_item(body=data)
                return func.HttpResponse(
                    json.dumps({"message": "Inserted successfully"}),
                    mimetype="application/json"
                )
            else:
                container.upsert_item(body=data)
                return func.HttpResponse(
                    json.dumps({"message": "Updated successfully"}),
                    mimetype="application/json"
                )

        # Read
        elif req.method == "GET":
            id = req.params.get("id")
            category = req.params.get("Category")

            if id and category:
                try:
                    item = container.read_item(item=id, partition_key=category)
                    return func.HttpResponse(
                        json.dumps(item),
                        mimetype="application/json"
                    )
                except exceptions.CosmosResourceNotFoundError:
                    return func.HttpResponse(
                        json.dumps({"error": "Item not found"}),
                        status_code=404,
                        mimetype="application/json"
                    )
            else:
                items = list(container.read_all_items())
                return func.HttpResponse(
                    json.dumps(items),
                    mimetype="application/json"
                )

        # Delete
        elif req.method == "DELETE":
            id = req.params.get("id")
            category = req.params.get("Category")
            if not id or not category:
                return func.HttpResponse(
                    json.dumps({"error": "Missing id or Category"}),
                    status_code=400,
                    mimetype="application/json"
                )

            try:
                container.delete_item(item=id, partition_key=category)
                return func.HttpResponse(
                    json.dumps({"message": "Deleted successfully"}),
                    mimetype="application/json"
                )
            except exceptions.CosmosResourceNotFoundError:
                return func.HttpResponse(
                    json.dumps({"error": "Item not found"}),
                    status_code=404,
                    mimetype="application/json"
                )

        # Invalid method
        return func.HttpResponse(
            json.dumps({"error": "Method not allowed"}),
            status_code=405,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error("Exception: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
