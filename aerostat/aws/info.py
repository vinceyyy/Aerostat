def info(event: dict, _) -> dict:
    with open("/opt/index.html", "r") as f:
        html = f.read()

    return {"statusCode": 200, "body": html, "headers": {"Content-Type": "text/html"}}
