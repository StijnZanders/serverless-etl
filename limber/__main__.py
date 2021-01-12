import click
from dotenv import load_dotenv
import os
import yaml
import json
from pathlib import Path
from .cli.generate_terraform import terraform
from .cli.utils.terraform import combine_configurations
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

    os.environ["CLOUD_FUNCTIONS_SERVICE_ACCOUNT_EMAIL"] = yaml_config["cloud"]["cloud_functions_service_account"]

    os.environ["TERRAFORM_ORGANIZATION"] = yaml_config["terraform"]["organization"]
    os.environ["TERRAFORM_WORKSPACE"] = yaml_config["terraform"]["workspace"]
    os.environ["TERRAFORM_SECRETS"] = json.dumps(yaml_config["terraform"]["secrets"])


def get_secrets():

    secrets = json.loads(os.environ["TERRAFORM_SECRETS"])

    secret_configs = []

    for secret_name in secrets:
        secret_config = {
            "resource": {
                "google_secret_manager_secret": [{
                    secret_name: {
                        "secret_id": secret_name,
                        "replication": {
                            "automatic": True
                        }
                    }
                }],
                "google_secret_manager_secret_version": [{
                    f"{secret_name}-version": {
                        "secret": f"${{google_secret_manager_secret.{secret_name}.id}}",
                        "secret_data": f"${{var.{secret_name}}}"
                    }
                }]
            },
            "variable": {
                f"{secret_name}": [{
                    "type": "string"
                }]
            }
        }

        secret_configs.append(secret_config)

    config = combine_configurations(secret_configs)

    return config


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
            yaml_config["cloud"]["provider"]: {
                "project": yaml_config["cloud"]["project"],
                "region": yaml_config["cloud"]["region"]
            }
        },
        "resource": {
            "google_storage_bucket": {
                "bucket": {
                    "name": yaml_config["cloud"]["default_bucket"],
                    "location": yaml_config["cloud"]["default_bucket_location"]
                }
            }

        },
        "terraform": {
            "backend": {
                "remote": {
                    "organization": os.environ["TERRAFORM_ORGANIZATION"],
                    "workspaces": {
                        "name": os.environ["TERRAFORM_WORKSPACE"]
                    }
                }
            }
        },
        "variable": {}
    }

    secrets = get_secrets()
    for resource in secrets["resource"]:
        config["resource"][resource] = secrets["resource"][resource]

    for variable in secrets["variable"]:
        config["variable"][variable] = secrets["variable"][variable]

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