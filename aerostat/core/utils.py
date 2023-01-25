import importlib.resources
import subprocess
from importlib.abc import Traversable

from rich import print


def find_static_resource_path(module: str, filename: str = None) -> Traversable:
    """Load Vega spec template from file"""
    try:
        m = importlib.resources.files(module)
        return m.joinpath(filename) if filename else m
    except Exception:
        raise ValueError(f"Cannot open {filename}")


def installed_check():
    """Check if a dependency are installed.
    This cannot be used as a decorator because the inner function would need to be registered with Typer.
    """
    try:
        for command in {"aws", "sam", "docker"}:
            subprocess.run(
                f"{command} --version", shell=True, check=True, capture_output=True
            )
    except FileNotFoundError as e:
        raise e


def docker_running_check():
    """Check if a dependency are installed.
    This cannot be used as a decorator because the inner function would need to be registered with Typer.
    """
    try:
        subprocess.run("docker info", shell=True, check=True, capture_output=True)
    except Exception as e:
        print(
            "[bold red]Docker is not running. Please start Docker and try again.[/bold red]"
        )
