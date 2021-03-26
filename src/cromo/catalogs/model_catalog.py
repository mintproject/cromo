import requests
from cromo.constants import MODEL_CATALOG_URL, DEFAULT_USERNAME

def getAllModelConfigurations():
    url = MODEL_CATALOG_URL + "/modelconfigurations?username=" + DEFAULT_USERNAME
    configs = requests.get(url=url).json()
    return configs
