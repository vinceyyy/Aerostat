import platform
import subprocess

from rich import print
from rich.progress import Progress

from deployer.libs.utils import find_static_resource_path


def is_windows():
    return platform.uname()[0] == "Windows"


def check_cli_dependency(command: str):
    """Check if a dependency are installed."""
    try:
        subprocess.run(f"{command} --version", shell=True, check=True, capture_output=True)
    except Exception:
        raise Exception(f"{command} is not installed")


def install_cli_dependencies():
    if not is_windows():
        raise NotImplementedError("Installing all dependencies via this tool is only supported on Windows")
    try:
        with find_static_resource_path("deployer.setup", "windows.ps1") as p:
            ps_script = p
            print(ps_script)
    except Exception as e:
        raise FileNotFoundError(f"Cannot find windows.ps1: {e}") from e
    subprocess.call([r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", ps_script])


def cli_install():
    """Check dependencies."""
    with Progress() as progress:
        task = progress.add_task("[bold green]Checking dependencies...", total=3)
        try:
            progress.update(task, advance=1)
            check_cli_dependency("aws")
            progress.update(task, advance=1)
            check_cli_dependency("sam")
            progress.update(task, advance=1)
            check_cli_dependency("docker")
            print("[bold green]All dependencies installed.[/bold green]")
        except Exception as e:
            progress.stop()
            print("\n[bold magenta]Installing dependencies... Please allow Access in the pop-up window[/bold magenta]")
            install_cli_dependencies()
