import importlib.resources
import os
import subprocess
from importlib.abc import Traversable


def run_serverless_command(command: str, cwd: str, env: dict = None):
    """Run a Serverless Framework command."""
    subprocess.run(
        f"serverless {command} --aws-profile aerostat",
        shell=True,
        check=True,
        cwd=cwd,
        env=env,
    )


def get_local_storage():
    """Initialize the local storage directory."""
    aerostat_dir = os.path.join(os.path.expanduser("~"), ".aerostat")
    if not os.path.exists(aerostat_dir):
        os.makedirs(aerostat_dir)
    return aerostat_dir


def find_static_resource_path(module: str, filename: str = "") -> Traversable:
    """Load Vega spec template from file"""
    try:
        return importlib.resources.files(module).joinpath(filename)
    except Exception:
        raise ValueError(f"Cannot open {filename}")
