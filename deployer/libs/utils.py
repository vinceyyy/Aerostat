from functools import partial
import importlib.resources
from importlib.abc import Traversable
from typing import Union

import dill
import pandas as pd

from deployer.libs.interfaces import Model


def find_static_resource_path(module: str, filename: str) -> Traversable:
    """Load Vega spec template from file"""
    try:
        return importlib.resources.files(module).joinpath(filename)
    except Exception:
        raise ValueError(f"Cannot open {filename}")


# wrap model's original scoring function with our function to be running when triggered
def run_predict(self, input_data: pd.DataFrame) -> Union[pd.DataFrame, pd.Series]:
    return self.predict(input_data)


def bundle_model(model: "RAW_Model", input_columns: list[str], target_path: str):
    """bundle a model with input column list"""
    setattr(model, run_predict.__name__, partial(run_predict, model))
    model.input_columns = input_columns

    try:
        with open(target_path, "wb") as f:
            dill.dump(model, f)
    except Exception as e:
        raise IOError(f"Failed to write model to {target_path}") from e
