import subprocess
from functools import partial
from typing import Union

import dill
import pandas as pd

from .interfaces import Model


# wrap model's original scoring function with our function to be running when triggered
def run_predict(self, input_data: pd.DataFrame) -> Union[pd.DataFrame, pd.Series]:
    return self.predict(input_data)


def bundle_model(model: "RAW_Model", input_columns: list[str], target_path: str) -> Model:
    """bundle a model with input column list"""
    setattr(model, run_predict.__name__, partial(run_predict, model))
    model.input_columns = input_columns

    try:
        with open(target_path, "wb") as f:
            dill.dump(model, f)
    except Exception as e:
        raise IOError(f"Failed to write model to {target_path}") from e


def check_dependencies():
    """Check if all dependencies are installed."""
    for command in {"aws", "sam", "docker"}:
        try:
            subprocess.check_output([command, "--version"])
        except FileNotFoundError:
            raise Exception(f"{command} is not installed")
