from typing import Optional

import questionary
import typer
from rich import print
from rich.progress import track

from deployer import __app_name__, __version__
from deployer.libs.build import build_image, get_system_dependencies
from deployer.libs.install import check_cli_dependency, install_cli_dependencies
from deployer.libs.login import get_aws_profiles, prompted_create_aws_profile
from deployer.libs.utils import pre_command_check

app = typer.Typer()


@app.command()
def install() -> None:
    """Install Docker and Serverless Framework if not installed."""
    dependencies = ["docker", "serverless"]
    try:
        for dependency in track(dependencies, "[bold green]Checking dependencies..."):
            check_cli_dependency(dependency)
        print("[bold green]All dependencies installed.[/bold green]")
    except Exception as e:
        print("\n[bold magenta]Installing dependencies... Please allow Access in the pop-up window[/bold magenta]")
        try:
            install_cli_dependencies()
        except NotImplementedError as e:
            print(f"[bold red]Error: {e}[/bold red]")
            raise typer.Exit(1)
        except FileNotFoundError as e:
            print(f"[bold red]Error: {e}[/bold red]")
            raise typer.Exit(1)


@app.command()
@pre_command_check
def login() -> None:
    """Configure AWS credentials for Serverless Framework."""
    use_existing = False
    profiles = get_aws_profiles()
    if len(profiles) == 0:
        print("[bold red]No AWS profile found. Please create AWS profile with access key first.[/bold red]")
    else:
        use_existing = typer.prompt("Existing AWS profiles detected, use existing ones?", type=bool)

    if use_existing:
        profile = questionary.select(
            "Select from existing AWS profile to use",
            choices=profiles).ask()  # returns value of selection
    else:
        profile = prompted_create_aws_profile()
    # TODO: use this profile for deploying


@app.command()
@pre_command_check
def build() -> None:
    """Build Docker image with model file, and set input columns as environment variables."""
    model_path = typer.prompt("Model pickle file path")
    # TODO: copy model file to docker context, since it cannot reference absolute path

    input_columns_str = typer.prompt("""Model input columns (type in as python list format ["col_1", "col_2", ...])""")
    try:
        input_columns = eval(input_columns_str)
    except Exception:
        raise Exception("""Input column list is not valid. Please input valid python list as ["col_1", "col_2", ...]""")

    python_dependencies_str = typer.prompt(
        """Machine Learning library used in model (type in as pip installable name, e.g. scikit-learn if sklearn is used)""")
    python_dependencies = python_dependencies_str.split(" ")

    try:
        build_image(model_path, input_columns, python_dependencies, get_system_dependencies(python_dependencies))
    except Exception as e:
        raise RuntimeError(f"Building docker image failed: {e}") from e


@app.command()
@pre_command_check
def deploy():
    """Deploy model to AWS Lambda with Serverless Framework."""
    pass


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
        version: Optional[bool] = typer.Option(
            None,
            "--version",
            "-v",
            help="Show the application's version and exit.",
            callback=_version_callback,
            is_eager=True,
        )
) -> None:
    return
