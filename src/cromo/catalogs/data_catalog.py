import requests
import json

from cromo.constants import DATA_CATALOG_URL

# Get all datasets having the given variables, and relevant for spatio-temporal information
def getMatchingDatasets(variables, geojson_file, start_date, end_date):
    with open(geojson_file) as fd:
        geojson = json.load(fd)
        response = requests.post(
            url= DATA_CATALOG_URL + "/datasets/find",
            json= {
                "standard_variable_names__in": variables,
                "spatial_coverage__intersects": geojson["geometry"],
                "start_time__lte": dateTimeToXSD(start_date),
                "end_time__gte": dateTimeToXSD(end_date),
                "limit": 100
            }
        )
        datasets = response.json()
        return datasets

def dateTimeToXSD(dt):
    return str(dt).replace(" ", "T")