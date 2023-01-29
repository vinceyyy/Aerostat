import subprocess

import typer
from rich import print

from aerostat.core.loginer import get_aws_profile_credentials


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
