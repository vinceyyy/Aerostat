import configparser
import os

import typer


def get_aws_credential_file():
    """Get AWS credentials from credential file as configparser object."""
    config = configparser.ConfigParser()
    try:
        with open(os.path.expanduser("~/.aws/credentials"), "r") as f:
            credentials = f.read()
            config.read_string(credentials)
            return config
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error: {e}") from e


def get_aws_profile_credentials(profile: str) -> dict:
    """Get AWS credentials from credential file as dictionary."""
    config = get_aws_credential_file()
    try:
        return {
            "aws_access_key_id": config[profile]["aws_access_key_id"],
            "aws_secret_access_key": config[profile]["aws_secret_access_key"],
        }
    except KeyError as e:
        raise KeyError(f"Error: {e}") from e


def create_aws_profile(profile_name: str, aws_access_key_id: str, aws_secret_access_key: str) -> None:
    """Create AWS profile with AWS credentials."""
    config = configparser.ConfigParser()
    config[profile_name] = {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key,
    }
    with open(os.path.expanduser("~/.aws/credentials"), "a") as f:
        config.write(f)


def prompted_create_aws_profile():
    """Prompt user to create AWS profile."""
    profile_name = "aerostat"
    aws_access_key_id = typer.prompt("AWS Access Key ID")
    aws_secret_access_key = typer.prompt("AWS Secret Access Key")
    create_aws_profile(profile_name, aws_access_key_id, aws_secret_access_key)
    return profile_name


if __name__ == "__main__":
    print(get_aws_profiles())
