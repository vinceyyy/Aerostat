import subprocess
import os

from aerostat.core.utils import OS


def _winget_install(app_id: str):
    return subprocess.run(
        [
            os.path.expanduser(r"~\AppData\Local\Microsoft\WindowsApps\winget.exe"),
            "install",
            "-e",
            "--accept-source-agreements",
            "--accept-package-agreements",
            "--id",
            app_id,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )


def nodejs_installer():
    if OS.is_windows():
        return _winget_install("OpenJS.NodeJS")
    if OS.is_mac():
        return subprocess.run(
            [
                "brew",
                "install",
                "node",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    raise NotImplementedError(
        "NodeJS installation is not supported on this operating system."
    )


def serverless_installer():
    if OS.is_windows():
        return subprocess.run(
            [
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                "npm",
                "install",
                "-g",
                "serverless@3.25.1",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    if OS.is_mac():
        return subprocess.run(
            ["npm", "install", "-g", "serverless@3.25.1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    raise NotImplementedError(
        "Serverless installation is not supported on this operating system."
    )


def docker_installer():
    if OS.is_windows():
        return _winget_install("Docker.DockerDesktop")
    if OS.is_mac():
        return subprocess.run(
            [
                "brew",
                "install",
                "--cask",
                "docker",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )


DEPENDENCIES = [
    {"name": "NodeJS", "command": "node", "installer": nodejs_installer},
    {"name": "Serverless", "command": "serverless", "installer": serverless_installer},
    {"name": "Docker-Desktop", "command": "docker", "installer": docker_installer},
]


def install_cli_dependencies(dependency_name: str = None):
    if OS.is_windows():
        raise NotImplementedError(
            "Installing all dependencies via this tool is only supported on Windows"
        )
    if not dependency_name:
        dependency_name = [d["name"] for d in DEPENDENCIES]
    for installer in [
        d["installer"] for d in DEPENDENCIES if d["name"] in dependency_name
    ]:
        installer()


if __name__ == "__main__":
    result = serverless_installer()
    print(result.stdout)
    print(result.stderr.decode("utf-8"))
