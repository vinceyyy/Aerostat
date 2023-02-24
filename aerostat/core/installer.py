import platform
import subprocess

from aerostat.core.utils import find_static_resource_path

DEPENDENCIES = [
    {"install_name": "docker-desktop", "command": "docker"},
    {"install_name": "serverless", "command": "serverless"},
]


def is_windows():
    return platform.uname()[0] == "Windows"


def install_cli_dependencies():
    if not is_windows():
        raise NotImplementedError(
            "Installing all dependencies via this tool is only supported on Windows"
        )
    try:
        with find_static_resource_path("aerostat.scripts", "setup_windows.ps1") as p:
            ps_script = p
    except Exception as e:
        raise FileNotFoundError(f"Cannot find setup_windows.ps1: {e}") from e
    subprocess.call(
        [
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            ps_script,
        ]
    )
