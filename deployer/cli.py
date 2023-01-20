import pickle
import uuid
from typing import Optional

import typer

from deployer import __app_name__, __version__
from .utils import check_dependencies, bundle_model

app = typer.Typer()

TMP_MODEL_PATH = f"{uuid.uuid4()}-model.pkl"


@app.command()
def init() -> None:
    """Check dependencies."""
    try:
        check_dependencies()
    except Exception as e:
        raise e
    # TODO: maybe don't need this if users can run in the same env as the model uses
    ml_library = typer.prompt("ML library used in this model (package name used in `pip install`)")
    import sys
    import subprocess

    # implement pip as a subprocess:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', ml_library])
    typer.echo(f"{ml_library} installed")


@app.command()
def bundle() -> None:
    """Bundle ML model with input column data"""
    try:
        check_dependencies()
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


def build():
    pass


def deploy():
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
