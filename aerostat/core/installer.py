import platform
import subprocess


def is_windows():
    return platform.uname()[0] == "Windows"


def nodejs_installer():
    subprocess.call(
        [
            r"C:\Users\VincentYan\AppData\Local\Microsoft\WindowsApps\winget.exe",
            "install",
            "-e",
            "--accept-source-agreements",
            "--accept-package-agreements",
            "--id",
            "OpenJS.NodeJS",
        ]
    )


def serverless_installer():
    subprocess.call(
        [
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "npm",
            "install",
            "-g",
            "serverless@3.25.1",
        ]
    )


def docker_installer():
    subprocess.call(
        [
            r"C:\Users\VincentYan\AppData\Local\Microsoft\WindowsApps\winget.exe",
            "install",
            "-e",
            "--accept-source-agreements",
            "--accept-package-agreements",
            "--id",
            "Docker.DockerDesktop",
        ]
    )


DEPENDENCIES = [
    {"name": "NodeJS", "command": "node", "installer": nodejs_installer},
    {"name": "Serverless", "command": "serverless", "installer": serverless_installer},
    {"name": "Docker-Desktop", "command": "docker", "installer": docker_installer},
]


def install_cli_dependencies(dependency_name: str = None):
    if not is_windows():
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
    install_cli_dependencies()
