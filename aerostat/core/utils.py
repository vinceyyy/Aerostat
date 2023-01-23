import subprocess
import importlib.resources
from importlib.abc import Traversable


def find_static_resource_path(module: str, filename: str) -> Traversable:
    """Load Vega spec template from file"""
    try:
        return importlib.resources.files(module).joinpath(filename)
    except Exception:
        raise ValueError(f"Cannot open {filename}")


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
