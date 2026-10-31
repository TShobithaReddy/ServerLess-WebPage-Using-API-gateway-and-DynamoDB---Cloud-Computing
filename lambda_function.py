"""
Lambda function for the registration form.

- POST /registrations  -> saves a new registration in DynamoDB
- GET  /registrations  -> returns the saved registrations

Before running: set an environment variable TABLE_NAME on the Lambda
function (for example: registrations).
"""
import json
import os
import uuid
from datetime import datetime, timezone

import boto3

# Connect to the DynamoDB table once, so it is reused between requests
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

# These headers let the browser accept the reply.
# (If CORS is also set in API Gateway, API Gateway uses its own settings.)
HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}


def reply(status, body):
    """Build the response that API Gateway expects."""
    return {"statusCode": status, "headers": HEADERS, "body": json.dumps(body, default=str)}


def get_method(event):
    """HTTP APIs and REST APIs name the method in different places."""
    return event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")


def save_registration(event):
    try:
        data = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return reply(400, {"error": "That was not valid JSON."})

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    roll_no = str(data.get("rollNo", "")).strip()

    # Basic checks so we don't store empty or broken entries
    if not name:
        return reply(400, {"error": "Please enter your name."})
    if "@" not in email or "." not in email:
        return reply(400, {"error": "Please enter a valid email."})

    item = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "rollNo": roll_no,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }

    try:
        table.put_item(Item=item)
    except Exception as error:
        print("Could not save to DynamoDB:", error)  # shows up in CloudWatch logs
        return reply(500, {"error": "Something went wrong while saving."})

    return reply(201, {"message": "Registered!", "id": item["id"]})


def list_registrations():
    try:
        result = table.scan(Limit=50)  # 50 is plenty for a small demo
    except Exception as error:
        print("Could not read from DynamoDB:", error)
        return reply(500, {"error": "Something went wrong while loading."})

    items = sorted(result.get("Items", []), key=lambda i: i.get("createdAt", ""), reverse=True)
    return reply(200, items)


def lambda_handler(event, context):
    method = get_method(event)

    if method == "OPTIONS":      # the browser's "is this allowed?" check
        return reply(200, {"message": "ok"})
    if method == "POST":
        return save_registration(event)
    if method == "GET":
        return list_registrations()

    return reply(405, {"error": "Method not allowed."})
