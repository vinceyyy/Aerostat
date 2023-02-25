import subprocess
import time

import typer
from rich import print
from rich.progress import track

from aerostat.core.installer import DEPENDENCIES
from aerostat.core.loginer import get_aws_profile_credentials
from aerostat.core.utils import OS


def installed_check(command: str = None):
    """Check if a dependency are installed.
    This cannot be used as a decorator because the inner function would need to be registered with Typer.
    """
    try:
        if not command:
            for command in track(
                [dependency["command"] for dependency in DEPENDENCIES],
                "[bold green]Checking dependencies...",
            ):
                subprocess.run(
                    f"{command} --version", shell=True, check=True, capture_output=True
                )
        else:
            subprocess.run(
                f"{command} --version", shell=True, check=True, capture_output=True
            )
    except ChildProcessError as e:
        print(
            f"[bold red]Dependencies not installed. Please run [bold blue]aerostat install[/bold blue] and try again.[/bold red]"
        )
        raise typer.Exit(1)


def loggedin_check():
    try:
        get_aws_profile_credentials("aerostat")
    except KeyError as e:
        print(
            "[bold red]You are not logged in. Please run [bold blue]aerostat login[/bold blue] and try again.[/bold red]"
        )
        raise typer.Exit(1)


def docker_running_check(verbose=False):
    """Check if a dependency are installed.
    This cannot be used as a decorator because the inner function would need to be registered with Typer.
    """
    try:
        subprocess.run("docker ps", shell=True, check=True, capture_output=True)
    except Exception as e:
        if verbose:
            print(
                "[bold red]Docker is not running. Please start Docker and try again.[/bold red]"
            )
        raise typer.Exit(1)


def start_docker_desktop():
    try:
        docker_running_check()
    except typer.Exit as e:
        print("[bold green]Starting Docker Desktop...[/bold green]")
        if OS.is_windows():
            subprocess.run(
                r"""powershell "& 'C:\Program Files\Docker\Docker\Docker Desktop.exe'""",
            )
        if OS.is_mac():
            subprocess.run(
                [
                    "open",
                    "-a",
                    "Docker",
                ],
            )
        count = 0
        while True:
            time.sleep(5)
            if count > 10:
                print("[bold red]Starting Docker failed.[/bold red]")
                raise RuntimeError("Starting Docker failed.")
            try:
                docker_running_check()
                break
            except Exception as e:
                count += 1


if __name__ == "__main__":
    start_docker_desktop()
