import os
import base64

from attachment_server import serve_excel


def info(event: dict, _) -> dict:
    if not event.get("queryStringParameters"):
        print("no query string parameters")
        with open("/opt/index.html", "r") as f:
            html = f.read()
        return {
            "statusCode": 200,
            "body": html,
            "headers": {"Content-Type": "text/html"},
        }

    api_endpoint = f"https://{event['headers']['host']}"
    input_columns = eval(os.getenv("INPUT_COLUMNS"))
    if not api_endpoint or not input_columns:
        return {
            "statusCode": 400,
            "body": "Missing api_endpoint or input_columns",
            "headers": {"Content-Type": "text/html"},
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/vnd.ms-excel.sheet.macroEnabled.12"},
        "isBase64Encoded": True,
        "body": base64.b64encode(
            serve_excel(
                column_names=input_columns,
                api_endpoint=api_endpoint,
            )
        ),
    }
