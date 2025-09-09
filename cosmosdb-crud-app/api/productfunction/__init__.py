import logging
import azure.functions as func
import os
import json
from azure.cosmos import CosmosClient, exceptions

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("ProductFunction triggered")
    try:
        # --- Cosmos DB setup inside main ---
        url = os.environ.get("COSMOS_URL")
        key = os.environ.get("COSMOS_KEY")
        database_name = os.environ.get("DATABASE_NAME")
        container_name = os.environ.get("COSMOS_CONTAINER_NAME")

        if not all([url, key, database_name, container_name]):
            return func.HttpResponse(
                json.dumps({"error": "Missing Cosmos DB environment variables"}),
                status_code=500,
                mimetype="application/json"
            )

        client = CosmosClient(url, credential=key)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        logging.info(f"Request method: {req.method}")

        # --- POST / PUT: Insert or update ---
        if req.method in ["POST", "PUT"]:
            try:
                data = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON"}),
                    status_code=400,
                    mimetype="application/json"
                )

            required_fields = ["id","name","Category","price"]
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
                    json.dumps({"message": "Inserted successfully", "item": data}),
                    status_code=201,
                    mimetype="application/json"
                )
            else:
                container.upsert_item(body=data)
                return func.HttpResponse(
                    json.dumps({"message": "Updated successfully", "item": data}),
                    status_code=200,
                    mimetype="application/json"
                )

        # --- GET: Read ---
        elif req.method == "GET":
            id = req.params.get("id")
            category = req.params.get("Category")

            if id and category:
                try:
                    item = container.read_item(item=id, partition_key=category)
                    return func.HttpResponse(
                        json.dumps(item),
                        status_code=200,
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
                    status_code=200,
                    mimetype="application/json"
                )

        # --- DELETE ---
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
                    status_code=200,
                    mimetype="application/json"
                )
            except exceptions.CosmosResourceNotFoundError:
                return func.HttpResponse(
                    json.dumps({"error": "Item not found"}),
                    status_code=404,
                    mimetype="application/json"
                )

        # --- Unsupported method ---
        return func.HttpResponse(
            json.dumps({"error": "Method not allowed"}),
            status_code=405,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Exception: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


