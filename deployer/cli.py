import pickle
from typing import Optional

import typer
from rich import print
from rich.progress import track

from deployer import __app_name__, __version__
from deployer.libs.install import check_cli_dependency, install_cli_dependencies
from deployer.libs.login import aws_login
from deployer.libs.build import build_image, get_system_dependencies
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
    aws_login()


@app.command()
@pre_command_check
def build() -> None:
    """Build Docker image with model file, and set input columns as environment variables."""
    try:
        pre_command_check()
    except Exception as e:
        raise e

    model_path = typer.prompt("Model pickle file path")
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Load model failed: {e}") from e

    input_columns_str = typer.prompt("""Model input columns (type in as python list format ["col_1", "col_2", ...])""")

    try:
        input_columns = eval(input_columns_str)
    except Exception:
        raise Exception(f"""Input column list is not valid. Please input valid python list as ["col_1", "col_2", ...]""")

    try:
        bundle_model(model, input_columns, TMP_MODEL_PATH)
    except IOError as e:
        raise RuntimeError(f"Write to tmp file failed: {e}") from e

    typer.echo("Model bundling finished.")
    raise typer.Exit()


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
