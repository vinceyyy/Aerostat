from typing import Optional

import questionary
import typer
from rich import print

from aerostat import __app_name__, __version__
from aerostat.core import deployer, installer, loginer
from aerostat.core.checks import installed_check, loggedin_check, docker_running_check
from aerostat.core.utils import get_deployment_info, list_deployments

app = typer.Typer()


@app.command()
def install() -> None:
    """Install dependencies needed for Aerostat.

    This command will install Chocolatey, Docker, and Serverless if they are not already installed.
    """
    try:
        installed_check()
        print("[bold green]All dependencies installed.[/bold green]")
    except Exception as e:
        print(
            "\n[bold magenta]Installing dependencies... This will invoke PowerShell and ask for admin permission. Please allow Access in the pop-up window[/bold magenta]"
        )
        try:
            installer.install_cli_dependencies()
        except NotImplementedError as e:
            print(f"[bold red]Error: {e}[/bold red]")
            raise typer.Exit(1)
        except FileNotFoundError as e:
            print(f"[bold red]Error: {e}[/bold red]")
            raise typer.Exit(1)


@app.command()
def login() -> None:
    """Configure AWS credentials for Aerostat to use.

    This command create or modifies ~/.aws/credentials, creating a new AWS profile named "Aerostat" if it does not exist.
    """
    installed_check()
    profiles = []
    cred_file = None

    try:
        cred_file = loginer.get_aws_credential_file()
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
            loginer.create_aws_profile(
                "aerostat",
                cred_file[profile]["aws_access_key_id"],
                cred_file[profile]["aws_secret_access_key"],
            )
            return

    if not cred_file or len(profiles) == 0:
        print(
            "[bold red]No AWS profile found. Please create AWS profile with access key first.[/bold red]"
        )
    else:
        print("[bold red]Input AWS credentials for Aerostat[/bold red]")
    loginer.prompted_create_aws_profile()

    print(
        "[bold green]AWS credentials for Aerostat configured successfully.[/bold green]"
    )


@app.command()
def deploy(
    model_path: str = typer.Option(
        ..., "--model-path", prompt="Model pickle file path"
    ),
    input_columns: str = typer.Option(
        ...,
        "--input-columns",
        prompt="""Model input columns - type in python list format like ["col_1", "col_2", ...]""",
    ),
    python_dependencies: str = typer.Option(
        ...,
        "--python-dependencies",
        prompt="""Machine Learning library used for the model (type in as pip installable name, e.g. scikit-learn if sklearn is used)""",
    ),
    project_name: str = typer.Option(
        "Aerostat", "--project-name", prompt="Name of the project"
    ),
):
    """Deploy model to AWS Lambda.

    This command uses Docker to build image locally, and deploys to AWS Lambda with Serverless Framework.
    It will blow up if Docker Desktop is not running.
    """
    installed_check()
    docker_running_check()
    loggedin_check()

    project_dir = deployer.init_project_dir(project_name)

    model_in_context = deployer.copy_model_file(model_path, project_dir)

    try:
        input_columns = eval(input_columns)
    except Exception:
        raise Exception(
            """Input column list is not valid. Please input valid python list as ["col_1", "col_2", ...]"""
        )

    python_dependencies = python_dependencies.split(" ")

    print("[bold green]Deploying to AWS Lambda...[/bold green]")

    deployer.deploy_to_aws(
        model_path=model_in_context,
        input_columns=input_columns,
        serverless_service_dir=project_dir,
        python_dependencies=python_dependencies,
        system_dependencies=deployer.get_system_dependencies(python_dependencies),
        service_name=project_name,
    )
    # TODO: capture returned api endpoint


@app.command()
def ls():
    """List all deployments exist locally.

    It looks for all directories in ~/.aerostat. Each directory is essentially a Serverless deployment artifact.
    """
    deployments = list_deployments()
    newline = "\n  • "
    print(
        f"""
[bold green]Found deployments:[/bold green]
  • {newline.join(deployments)}
"""
    )


@app.command()
def info(project_name: Optional[str] = typer.Argument(None)) -> None:
    """Show information about a specific deployment."""
    deployments = list_deployments()
    if project_name:
        if project_name not in deployments:
            print(
                f"[bold red]Deployment {project_name} not found. Please check with aerostat ls.[/bold red]"
            )
            raise typer.Exit(1)
        return get_deployment_info(project_name)

    selected_project = questionary.select(
        "Select from existing deployments", choices=deployments
    ).ask()

    return get_deployment_info(selected_project)


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
