import click
from dotenv import load_dotenv
import os
import yaml
import subprocess
import json
from pathlib import Path
from .cli.generate_terraform import terraform
load_dotenv()

TERRAFORM_DIRECTORY = "terraform_plan"
CONFIG_FILE = "limber.yaml"

@click.group()
def cli():
    """
    Just the main cli
    """
    load_environment_variables()


def load_environment_variables():
    absolute_config_file = os.path.abspath(CONFIG_FILE)

    with open(absolute_config_file) as file:
        yaml_config = yaml.safe_load(file.read())

    with open(yaml_config["cloud"]["key_file"]) as file:
        key_file = json.loads(file.read())

    os.environ["SERVICE_ACCOUNT_EMAIL"] = key_file["client_email"]
    os.environ["CLOUD_FUNCTIONS_SERVICE_ACCOUNT_EMAIL"] = yaml_config["cloud"]["cloud_functions_service_account"]


@cli.command("init")
def init():
    """
    Intializes Limber
    """

    # Create a folder for the output
    Path(TERRAFORM_DIRECTORY).mkdir(exist_ok=True)

    # Create initial terraform config there
    absolute_config_file = os.path.abspath(CONFIG_FILE)

    with open(absolute_config_file) as file:
        yaml_config = yaml.safe_load(file.read())

    config = {
        "provider": {
            yaml_config["cloud"]["provider"]:
                {
                    "credentials": os.path.abspath(yaml_config["cloud"]["key_file"]),
                    "project": yaml_config["cloud"]["project"],
                    "region": yaml_config["cloud"]["region"]
                }
        },
        "resource": {
            "google_storage_bucket": {
                "bucket": {
                    "name": yaml_config["cloud"]["default_bucket"]
                }
            }
        }
    }

    provider_config = f"{TERRAFORM_DIRECTORY}/provider.tf.json"
    with open(provider_config,"w") as file:
        file.write(json.dumps(config, indent=4, sort_keys=False))

    print("Limber has now successfully initialized using your configuration")

t = terraform(folder="terraform_plan")

@cli.command("plan")
def plan():
    """
    Create a plan for infra
    """
    t.create_terraform_configuration()


if __name__ == '__main__':
    cli()