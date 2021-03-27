from pathlib import Path

from click.types import DateTime

import re
import cromo
import semver
import click
from cromo import _utils
from cromo._utils import get_cromo_logger
from cromo.catalogs.data_catalog import getMatchingDatasets
from cromo.catalogs.model_catalog import getModelConfigurationDetails, getAllModelConfigurations

logging = get_cromo_logger()


@click.group()
@click.option("--verbose", "-v", default=0, count=True)
def cli(verbose):
    _utils.init_logger()
    try:
        lv = ".".join(_utils.get_latest_version().split(".")[:3])
    except Exception as e:
        click.secho(
            f"""WARNING: Unable to check if cromo is updated""",
            fg="yellow",
        )
        return

    cv = ".".join(cromo.__version__.split(".")[:3])

    if semver.compare(lv, cv) > 0:
        click.secho(
            f"""WARNING: You are using cromo version {cromo.__version__}, however version {lv} is available.
You should consider upgrading via 'pip install --upgrade cromo' command.""",
            fg="yellow",
        )


@cli.command(short_help="Find appropriate models for a particular scenario and region")
@click.argument(
    "scenario",
    default="ControlledFire",
    required=True
)
@click.argument(
    "region_geojson",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, resolve_path=True),
    default=Path('src/cromo/test/awash.geojson'),
    required=True
)
@click.argument(
    "start_date",
    type=click.DateTime(),
    default=DateTime(),
    required=True
)
@click.argument(
    "end_date",
    type=click.DateTime(),
    default=DateTime(),
    required=True
)
def start(scenario, region_geojson, start_date, end_date):
    print(region_geojson)
    print(start_date)
    print(end_date)

    configs = find_models(scenario)
    # For each model, get input details
    for config in configs:
        print("Model: {}".format(config.label))
        config = getModelConfigurationDetails(config)
        if config.has_input is not None:
            for input in config.has_input:
                #print(input)
                if input.has_presentation is not None:
                    print("\t - Input: {}".format(input.label[0]))
                    variables = []
                    for pres in input.has_presentation:
                        if pres.has_standard_variable is not None:
                            variables.append(pres.has_standard_variable[0].label[0])
                    print("\t - Variables: {}".format(str(variables)))
                    datasets = getMatchingDatasets(variables, region_geojson, start_date, end_date)
                    print(datasets)
    

def find_models(scenario):
    # Get all matching model configurations (or setups ?)
    print ("Fetching all model configurations for {}".format(scenario))
    configs = getAllModelConfigurations()
    matching_configs = []
    for config in configs:
        if config.description:
            if re.search(scenario, config.description[0], re.IGNORECASE):
                matching_configs.append(config)
            elif re.search(scenario, config.label[0], re.IGNORECASE):
                matching_configs.append(config)
    return matching_configs
