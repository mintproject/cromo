from json.encoder import JSONEncoder
from pathlib import Path

from click.types import DateTime

import re
import cromo
import semver
import click
from cromo import _utils
from cromo._utils import get_cromo_logger
from cromo.catalogs.data_catalog import getMatchingDatasetResources, getMatchingDatasets
from cromo.catalogs.model_catalog import getAllModelConfigurationSetups, getModelConfigurationDetails, getAllModelConfigurations

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
    print("SEARCH MODELS")
    print("- Scenario: {}".format(scenario))
    print("- GeoJSON: {}".format(region_geojson))
    print("- Start Date: {}, End Date: {}\n".format(start_date, end_date))

    print("Searching models...", end='\r')

    configs = find_models(scenario)
    
    print("{}".format(''.join([' ']*100)), end='\r') # Clear line

    # For each model, get input details
    for config in configs:
        print("\n{}\n{}".format(config.label[0], "="*len(config.label[0])))
        config = getModelConfigurationDetails(config)
        if config.has_input is not None:
            for input in config.has_input:
                #print(input)
                if input.has_presentation is not None:
                    print("\tInput: {}".format(input.label[0]))
                    variables = []
                    for pres in input.has_presentation:
                        if pres.has_standard_variable is not None:
                            variables.append(pres.has_standard_variable[0].label[0])
                    print("\tVariables: {}".format(str(variables)))

                    print("\t\tSearching datasets...", end='\r')

                    datasets = getMatchingDatasets(variables, region_geojson, start_date, end_date)
                    
                    print("{}".format(''.join([' ']*100)), end='\r') # Clear line

                    if len(datasets) == 0:
                        print("\r\t\tNo datasets found in data catalog matching input variables")
                    else:
                        matches = match_typed_datasets(datasets, input.type)
                        if len(matches) == 0:
                            print("\r\t\tNo datasets found in data catalog for matching type. Showing all datasets for matching input variables")
                            matches = datasets
                        for ds in matches:
                            meta = ds["dataset_metadata"]
                            print("\r\t\t* {}".format(ds["dataset_name"]))
                            if "source" in meta:
                                print("\t\t\t- Source: {}".format(meta["source"]))
                            if "version" in meta:
                                print("\t\t\t- Version: {}".format(meta["version"]))

                            print("\t\t\t- Fetching resources...", end='\r')

                            resources = getMatchingDatasetResources(ds["dataset_id"], region_geojson, start_date, end_date)
                            
                            print("{}".format(''.join([' ']*100)), end='\r') # Clear line
                            print("\r\t\t\t- {} resources".format(len(resources)))
        else:
            print("\tNo Inputs for this model")
    

def match_typed_datasets(datasets, types):
    matches = []
    for ds in datasets:
        if "datatype" in ds["dataset_metadata"]:
            dtype = "https://w3id.org/wings/export/MINT#{}".format(ds["dataset_metadata"]["datatype"])
            if dtype in types:
                matches.append(ds)
    return matches

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
