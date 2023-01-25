import shutil
import subprocess

from aerostat.core.utils import find_static_resource_path


def copy_model_file(model_path: str) -> str:
    """copy model file to current directory"""
    try:
        aws_module = find_static_resource_path("aerostat.aws")
        target_path = aws_module.joinpath("model.pkl")
        shutil.copy(model_path, str(target_path))
    except Exception as e:
        raise Exception(f"Failed to copy model file to current directory: {e}")


def build_image(model_path: str, input_columns: list[str], dockerfile_path: str, python_dependencies: list[str],
                system_dependencies: list[str]) -> None:
    """bundle a model with input column list"""
    sys_dep_str = f"""--build-arg SYSTEM_DEPENDENCIES={" ".join(system_dependencies)}""" if system_dependencies else ""

    try:
        subprocess.call(f"""docker build -t MLSheet \
         --build-arg MODEL_PATH="{model_path}" \
         --build-arg PYTHON_DEPENDENCIES="{" ".join(python_dependencies)}" \
         --build-arg INPUT_COLUMNS="{input_columns}" \
         {sys_dep_str} \
         {dockerfile_path}""", shell=True)
    except Exception as e:
        raise Exception(f"Failed to build docker image, please make sure docker desktop is running: {e}")


def get_system_dependencies(python_dependencies: list[str]) -> list[str]:
    """get system dependencies from certain ML libraries"""
    system_dependencies = []
    if "lightgbm" in [s.lower() for s in python_dependencies]:
        system_dependencies.append("libgomp1")
    return system_dependencies
