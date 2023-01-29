import os
import shutil

from aerostat.core.utils import find_static_resource_path, run_serverless_command


def copy_model_file(model_path: str):
    """copy model file to current directory"""
    try:
        with find_static_resource_path("aerostat.aws", "model.pkl") as target_path:
            shutil.copy(model_path, str(target_path))
        return "model.pkl"
    except Exception as e:
        raise Exception(f"Failed to copy model file to current directory: {e}")


def get_serverless_service_dir():
    """get serverless config file"""
    return find_static_resource_path("aerostat.aws").joinpath("")


def deploy_to_aws(
    service_name: str,
    model_path: str,
    input_columns: list[str],
    serverless_service_dir: str,
    python_dependencies: list[str],
    system_dependencies: list[str],
) -> None:
    """bundle a model with input column list"""
    env = {
        **os.environ.copy(),
        "SERVICE_NAME": service_name,
        "MODEL_PATH": model_path,
        "INPUT_COLUMNS": f"""["{'","'.join(input_columns)}"]""",
        "PYTHON_DEPENDENCIES": " ".join(python_dependencies),
        "SYSTEM_DEPENDENCIES": " ".join(system_dependencies),
    }

    try:
        run_serverless_command(command="deploy", env=env, cwd=serverless_service_dir)

    except Exception as e:
        raise Exception(
            f"Failed to build docker image, please make sure docker desktop is running: {e}"
        )


def get_system_dependencies(python_dependencies: list[str]) -> list[str]:
    """get system dependencies from certain ML libraries"""
    system_dependencies = []
    if "lightgbm" in [s.lower() for s in python_dependencies]:
        system_dependencies.append("libgomp1")
    return system_dependencies
