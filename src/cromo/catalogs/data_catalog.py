import requests
import json

from cromo.constants import DATA_CATALOG_URL

# Get all datasets having the given variables that are relevant for the provided spatio-temporal information
def getMatchingDatasets(variables, geojson_file, start_date, end_date):
     with open(geojson_file) as fd:
        geojson = json.load(fd)
        data = {
            "standard_variable_names__in": variables,
            "spatial_coverage__intersects": geojson["geometry"],
            "start_time__lte": dateTimeToXSD(start_date),
            "end_time__gte": dateTimeToXSD(end_date),
            "limit": 100
        }
        response = requests.post(
            url= DATA_CATALOG_URL + "/datasets/find",
            json= data
        )
        response = response.json()
        if "result" in response and response["result"] == "success":
            return response["datasets"]
        return []

# Get all resources for a dataset that are relevant for the provided spatio-temporal information
def getMatchingDatasetResources(dsid, geojson_file, start_date, end_date):
    with open(geojson_file) as fd:
        geojson = json.load(fd)
        data = {
            "dataset_id": dsid,
            "filter": {
                "spatial_coverage__intersects": geojson["geometry"],
                "start_time__lte": dateTimeToXSD(start_date),
                "end_time__gte": dateTimeToXSD(end_date)
            },
            "limit": 5000            
        }
        response = requests.post(
            url= DATA_CATALOG_URL + "/datasets/dataset_resources",
            json= data
        )
        response = response.json()
        if "result" in response and response["result"] == "success":
            return response["dataset"]["resources"]
        return []


def dateTimeToXSD(dt):
    return str(dt).replace(" ", "T")