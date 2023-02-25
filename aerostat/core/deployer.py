import os
import shutil
from datetime import datetime

import jinja2

from aerostat.core.utils import (
    find_static_resource_path,
    run_serverless_command,
    get_local_aerostat_folder,
    sanitize_service_name,
    get_module_version,
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


def init_project_dir(project_name: str) -> str:
    """Initialize a new project directory."""
    local_storage = get_local_aerostat_folder()
    project_dir = os.path.join(local_storage, project_name)

    if os.path.exists(project_dir):
        return project_dir

    cloud_template_dir = str(find_static_resource_path("aerostat.aws"))
    static_layer_dir = str(find_static_resource_path("aerostat.static"))
    try:
        shutil.copytree(src=cloud_template_dir, dst=project_dir)
        shutil.copytree(src=static_layer_dir, dst=os.path.join(project_dir, "static"))
    except Exception as e:
        raise Exception(f"Failed to copy template to project directory: {e}")

    return project_dir


def render_html(
    project_name: str,
    input_columns: list[str],
    python_dependencies: list[str],
    save_to: str = None,
):
    environment = jinja2.Environment()
    template = environment.from_string(
        find_static_resource_path("aerostat.static", "index.html").read_text(
            encoding="utf-8"
        )
    )
    result = template.render(
        project_name=project_name,
        build_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        input_columns=input_columns,
        python_dependencies=python_dependencies,
        aerostat_version=get_module_version(),
    )

    if save_to:
        os.makedirs(os.path.dirname(save_to), exist_ok=True)
        with open(save_to, "w") as f:
            f.write(result)

    return result


def deploy_to_aws(
    service_name: str,
    model_path: str,
    input_columns: list[str],
    serverless_service_dir: str,
    python_dependencies: list[str],
    system_dependencies: list[str],
) -> None:
    """bundle a model with input column list"""
    render_html(
        project_name=service_name,
        input_columns=input_columns,
        python_dependencies=python_dependencies,
        save_to=os.path.join(serverless_service_dir, "static", "index.html"),
    )
    env = {
        **os.environ.copy(),
        "SERVICE_NAME": sanitize_service_name(service_name),
        "MODEL_PATH": model_path,
        "INPUT_COLUMNS": f"""["{'","'.join(input_columns)}"]""",
        "PYTHON_DEPENDENCIES": " ".join(python_dependencies),
        "SYSTEM_DEPENDENCIES": " ".join(system_dependencies),
    }

    return run_serverless_command(command="deploy", env=env, cwd=serverless_service_dir)


def get_system_dependencies(python_dependencies: list[str]) -> list[str]:
    """get system dependencies from certain ML libraries"""
    system_dependencies = []
    if "lightgbm" in [s.lower() for s in python_dependencies]:
        system_dependencies.append("libgomp1")
    return system_dependencies


if __name__ == "__main__":
    print(get_module_version())
