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


def list_deployments():
    """List deployments from local storage"""
    local_storage = get_local_storage()
    return [
        n
        for n in os.listdir(local_storage)
        if os.path.isdir(os.path.join(local_storage, n))
    ]


def get_deployment_info(project_name: str):
    """Get deployment info from local storage"""
    local_storage = get_local_storage()
    project_dir = os.path.join(local_storage, project_name)
    if not os.path.exists(project_dir):
        raise Exception("Deployment info not found. Please deploy first.")

    return run_serverless_command("info", cwd=project_dir)
