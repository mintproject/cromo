from cromo.catalogs.model_catalog import checkConfigViability, getAllModelConfigurations
from cromo._utils import parse_datetime
import re

def checkModelConfigurationValidity(configId, body):
    return checkConfigViability(
        configId, 
        body["spatial"], 
        parse_datetime(body["temporal"]["start_date"]),
        parse_datetime(body["temporal"]["end_date"]))


def fetchModelConfigurationsForScenario(scenario):
    # Get all matching model configurations (or setups ?)
    configs = getAllModelConfigurations()
    matching_configs = []
    for config in configs:
        if config.description:
            if (re.search(scenario, config.description[0], re.IGNORECASE) or 
                re.search(scenario, config.label[0], re.IGNORECASE)):
                matching_configs.append({
                    "id": config.id,
                    "name": config.label[0]})
    return matching_configs