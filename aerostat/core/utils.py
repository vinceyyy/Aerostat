import importlib.resources
import os
import subprocess
from importlib.abc import Traversable

import typer
from rich import print

from aerostat.core.login import get_aws_profile_credentials


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
        print(
            f"[bold red]Dependencies not installed. Please run [bold blue]aerostat install[/bold blue] and try again.[/bold red]"
        )
        raise typer.Exit(1)


def loggedin_check():
    try:
        get_aws_profile_credentials("aerostat")
    except Exception as e:
        print(
            "[bold red]You are not logged in. Please run [bold blue]aerostat login[/bold blue] and try again.[/bold red]"
        )
        raise typer.Exit(1)


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
        raise typer.Exit(1)


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
