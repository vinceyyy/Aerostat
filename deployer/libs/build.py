import subprocess


def build_image(model_path: str, input_columns: list[str], dockerfile_path: str, python_dependencies: list[str],
                system_dependencies: list[str]) -> None:
    """bundle a model with input column list"""
    sys_dep_str = f"""--build-arg SYSTEM_DEPENDENCIES={" ".join(system_dependencies)}""" if system_dependencies else ""

    subprocess.call(f"""docker build -t MLSheet \
     --build-arg MODEL_PATH="{model_path}" \
     --build-arg PYTHON_DEPENDENCIES="{" ".join(python_dependencies)}" \
     --build-arg INPUT_COLUMNS="{input_columns}" \
     {sys_dep_str} \
     {dockerfile_path}""", shell=True)


def get_system_dependencies(python_dependencies: list[str]) -> list[str]:
    """get system dependencies from certain ML libraries"""
    system_dependencies = []
    if "lightgbm" in [s.lower() for s in python_dependencies]:
        system_dependencies.append("libgomp1")
    return system_dependencies
