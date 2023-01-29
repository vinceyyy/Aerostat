import json
import os
import pickle

import pandas as pd


def predict(event: dict, _) -> dict:
    """Lambda handler for the aws function.
    This function returns a result, along with all columns that are not specified in input_cols.

    :param event: API Gateway Lambda Proxy Input Format: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
    :param _: Lambda Context runtime methods and attributes: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    :return: API Gateway Lambda Proxy Output Format: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    request_body = json.loads(
        event["body"]
    )  # request_body as {column_1: [value1, value2, ...], column_2: [value1, value2, ...], ...}
    df = pd.DataFrame(request_body)

    # locate model file
    model_path = f"{os.getenv('FUNCTION_DIR')}/model.pkl"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    # Load the model
    with open(model_path, "rb") as f:
        try:
            model = pickle.load(f)
            print("Model loaded")
        except Exception as e:
            raise RuntimeError(f"Loading model failed: {e}")

    # load input columns
    input_columns = eval(os.getenv("INPUT_COLUMNS"))
    if not isinstance(input_columns, list):
        raise ValueError("Input columns must be a list")

    # Run prediction
    prediction_result = model.predict(df[input_columns])

    # if only one column is returned, name it as result
    prediction_df = pd.DataFrame(prediction_result)
    if prediction_df.shape[1] == 1:
        prediction_df.columns = ["result"]

    total_result = pd.concat([df.drop(columns=input_columns), prediction_df], axis=1)

    # Attach unused columns to result. Most likely those are used as id.
    response_body = total_result.to_dict(
        orient="list"
    )  # response_body as {column_1: [value1, value2, ...], column_2: [value1, value2, ...], ...}

    return {"statusCode": 200, "body": json.dumps(response_body)}


def info(event: dict, _) -> dict:
    with open(f"{os.getenv('FUNCTION_DIR')}/index.html", "r") as f:
        html = f.read()

    return {"statusCode": 200, "body": html, "headers": {"Content-Type": "text/html"}}
