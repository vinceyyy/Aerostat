import os
import shutil

from aerostat.core.utils import (
    find_static_resource_path,
    run_serverless_command,
    get_local_storage,
)


def copy_model_file(model_path: str, project_dir: str):
    """copy model file to current directory"""
    model_name = "model.pkl"
    target_path = os.path.join(project_dir, model_name)
    try:
        shutil.copy(model_path, target_path)
        return model_name
    except Exception as e:
        raise Exception(f"Failed to copy model file to current directory: {e}")


def get_project_dir(project_name: str) -> str:
    """Initialize a new project directory."""
    local_storage = get_local_storage()
    project_dir = os.path.join(local_storage, project_name)

    if os.path.exists(project_dir):
        return project_dir

    template_dir = str(find_static_resource_path("aerostat.aws"))
    try:
        shutil.copytree(src=template_dir, dst=project_dir)
    except Exception as e:
        raise Exception(f"Failed to copy template to project directory: {e}")

    return project_dir


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
