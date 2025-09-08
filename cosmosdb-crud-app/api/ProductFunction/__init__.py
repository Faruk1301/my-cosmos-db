import logging
import azure.functions as func
import os
import json
from azure.cosmos import CosmosClient

url = os.environ["COSMOS_URL"]
key = os.environ["COSMOS_KEY"]
database_name = os.environ["DATABASE_NAME"]
container_name = os.environ["COSMOS_CONTAINER_NAME"]

client = CosmosClient(url, credential=key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    method = req.method

    try:
        if method == "POST":
            data = req.get_json()
            # Required fields
            required_fields = ["id", "name", "Category", "price"]
            missing = [f for f in required_fields if f not in data]

            if missing:
                error_msg = f"Missing fields: {', '.join(missing)}"
                logging.error(error_msg)
                return func.HttpResponse(error_msg, status_code=400)

            container.create_item(body=data)
            return func.HttpResponse("Inserted successfully", status_code=200)

        elif method == "PUT":
            data = req.get_json()
            required_fields = ["id", "name", "Category", "price"]
            missing = [f for f in required_fields if f not in data]

            if missing:
                error_msg = f"Missing fields: {', '.join(missing)}"
                logging.error(error_msg)
                return func.HttpResponse(error_msg, status_code=400)

            container.upsert_item(body=data)
            return func.HttpResponse("Updated successfully", status_code=200)

        elif method == "GET":
            id = req.params.get("id")
            category = req.params.get("Category")

            if id and category:
                # Return single item
                item = container.read_item(item=id, partition_key=category)
                return func.HttpResponse(json.dumps(item), mimetype="application/json")
            else:
                # Return all items if no id/category
                items = list(container.read_all_items())
                return func.HttpResponse(json.dumps(items, indent=2), mimetype="application/json")

        elif method == "DELETE":
            id = req.params.get("id")
            category = req.params.get("Category")
            if not id or not category:
                return func.HttpResponse("Missing id or Category", status_code=400)

            container.delete_item(item=id, partition_key=category)
            return func.HttpResponse("Deleted successfully", status_code=200)

        else:
            return func.HttpResponse("Unsupported method", status_code=405)

    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

