from functools import partial
import importlib.resources
from importlib.abc import Traversable
from typing import Union

import dill
import pandas as pd


def find_static_resource_path(module: str, filename: str) -> Traversable:
    """Load Vega spec template from file"""
    try:
        return importlib.resources.files(module).joinpath(filename)
    except Exception:
        raise ValueError(f"Cannot open {filename}")


# wrap model's original scoring function with our function to be running when triggered
def run_predict(self, input_data: pd.DataFrame) -> Union[pd.DataFrame, pd.Series]:
    return self.predict(input_data)





def pre_command_check(f):
    """Check if a dependency are installed."""

    def wrapper(*args, **kwargs):
        try:
            for command in {"aws", "sam", "docker"}:
                subprocess.run(f"{command} --version", shell=True, check=True, capture_output=True)
        except FileNotFoundError as e:
            raise e
        f(*args, **kwargs)

    return wrapper