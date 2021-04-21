from cromo.catalogs.model_catalog import checkConfigViability
from cromo._utils import parse_datetime

def checkConfigValidityAPI(configId, body):
    return checkConfigViability(
        configId, 
        body["spatial"], 
        parse_datetime(body["temporal"]["start_date"]),
        parse_datetime(body["temporal"]["end_date"]))