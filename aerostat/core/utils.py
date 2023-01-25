import importlib.resources
import subprocess
from importlib.abc import Traversable


def find_static_resource_path(module: str, filename: str = None) -> Traversable:
    """Load Vega spec template from file"""
    try:
        m = importlib.resources.files(module)
        return m.joinpath(filename) if filename else m
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
