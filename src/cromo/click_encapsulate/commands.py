from pathlib import Path

from click.types import DateTime

import geojson
import re
import cromo
import semver
import click
from cromo import _utils
from cromo._utils import get_cromo_logger
from cromo.catalogs.model_catalog import checkConfigViability, getAllModelConfigurations, getModelRulesFromFile
from cromo.constants import ONTOLOGY_DIR, RULES_DIR

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
    "geojson_file",
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
@click.option('--rulesdir', prompt='Rules Directory',
              help='The directory that contains the model rules', required=True, default=RULES_DIR, show_default=True)
@click.option('--ontdir', prompt='Ontology Directory',
              help='The directory that contains the execution ontology', required=True, default=ONTOLOGY_DIR, show_default=True)

def start(scenario, geojson_file, start_date, end_date, rulesdir, ontdir):
    print("SEARCH MODELS")
    print("- Scenario: {}".format(scenario))
    print("- GeoJSON File: {}".format(geojson_file))
    print("- Start Date: {}, End Date: {}\n".format(start_date, end_date))

    print("Searching models...", end='\r')
    configs = find_models(scenario)
    print("{}".format(''.join([' ']*100)), end='\r') # Clear line

    with open(geojson_file) as fd:
        region_geojson = geojson.load(fd)
        # For each model, get input details
        for config in configs:
            checkConfigViability(config.id, region_geojson, start_date, end_date, rulesdir=rulesdir, ontdir=ontdir)
            #print(viability)


def find_models(scenario):
    # Get all matching model configurations (or setups ?)
    configs = getAllModelConfigurations()
    #print ("Fetching all model configuration setups for {}".format(scenario))
    #configs = getAllModelConfigurationSetups()    
    matching_configs = []
    for config in configs:
        if config.description:
            if re.search(scenario, config.description[0], re.IGNORECASE):
                matching_configs.append(config)
            elif re.search(scenario, config.label[0], re.IGNORECASE):
                matching_configs.append(config)
    return matching_configs
