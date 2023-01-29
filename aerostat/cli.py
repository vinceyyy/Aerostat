from typing import Optional

import questionary
import typer
from rich import print
from rich.progress import track

from aerostat import __app_name__, __version__
from aerostat.core.install import check_cli_dependency, install_cli_dependencies
from aerostat.core.login import (
    prompted_create_aws_profile,
    get_aws_credential_file,
    create_aws_profile,
)
from aerostat.core.deploy import (
    get_serverless_service_dir,
    get_system_dependencies,
    deploy_to_aws,
    copy_model_file,
)
from aerostat.core.utils import installed_check, docker_running_check

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
        print(
            "\n[bold magenta]Installing dependencies... Please allow Access in the pop-up window[/bold magenta]"
        )
        try:
            install_cli_dependencies()
        except NotImplementedError as e:
            print(f"[bold red]Error: {e}[/bold red]")
            raise typer.Exit(1)
        except FileNotFoundError as e:
            print(f"[bold red]Error: {e}[/bold red]")
            raise typer.Exit(1)


@app.command()
def login() -> None:
    """Configure AWS credentials for Serverless Framework."""
    installed_check()
    profiles = []
    cred_file = None

    try:
        cred_file = get_aws_credential_file()
        profiles = cred_file.sections()
    except FileNotFoundError as e:
        pass

    if len(profiles) > 0:
        if "aerostat" in profiles:
            print("[bold green]Aerostat already logged in.[/bold green]")
            return

        use_existing = questionary.confirm(
            "Existing AWS profiles detected, use existing ones?"
        ).ask()
        # if using existing profile, copy profile to aerostat
        if use_existing:
            profile = questionary.select(
                "Select from existing AWS profile to use", choices=profiles
            ).ask()  # returns value of selection
            create_aws_profile(
                "aerostat",
                cred_file[profile]["aws_access_key_id"],
                cred_file[profile]["aws_secret_access_key"],
            )
            return

    if cred_file is None or len(profiles) == 0:
        print(
            "[bold red]No AWS profile found. Please create AWS profile with access key first.[/bold red]"
        )
    else:
        print("[bold red]Input AWS credentials for Aerostat[/bold red]")
    prompted_create_aws_profile()

    print(
        "[bold green]AWS credentials for Aerostat configured successfully.[/bold green]"
    )


@app.command()
def deploy():
    """Deploy model to AWS Lambda with Serverless Framework."""
    installed_check()
    docker_running_check()

    serverless_service_dir = str(get_serverless_service_dir()).strip()

    model_path = typer.prompt("Model pickle file path").strip()
    model_in_context = copy_model_file(model_path)

    input_columns_str = typer.prompt(
        """Model input columns (type in as python list format ["col_1", "col_2", ...])"""
    )
    try:
        input_columns = eval(input_columns_str)
    except Exception:
        raise Exception(
            """Input column list is not valid. Please input valid python list as ["col_1", "col_2", ...]"""
        )

    python_dependencies_str = typer.prompt(
        """Machine Learning library used in model (type in as pip installable name, e.g. scikit-learn if sklearn is used)"""
    )
    python_dependencies = python_dependencies_str.split(" ")

    print("[bold green]Deploying to AWS Lambda...[/bold green]")

    deploy_to_aws(
        model_path=model_in_context,
        input_columns=input_columns,
        serverless_service_dir=serverless_service_dir,
        python_dependencies=python_dependencies,
        system_dependencies=get_system_dependencies(python_dependencies),
        service_name=service_name,
    )
    # TODO: capture returned api endpoint


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
