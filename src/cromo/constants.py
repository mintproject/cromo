GIT_DIRECTORY = ".git"
FORMAT_KEY = "format"
CROMO_DEFAULT_PATH = "/tmp/cromo/"
CROMO_DIR = "/tmp/cromo/"
LOG_FILE = "log.txt"

RULES_DIR = "src/cromo/resources/rules"
ONTOLOGY_DIR = "src/cromo/resources/ontology"
EXECUTION_ONTOLOGY_URL = "https://w3id.org/mint/execution.owl"

#DEFAULT_USERNAME = f"mint@isi.edu"
DEFAULT_USERNAME = f"wildfire@isi.edu"
MODEL_CATALOG_URL = f"https://api.models.wildfire.mint.isi.edu/v1.7.0"
#MODEL_CATALOG_URL = f"https://api.models.mint.isi.edu/v1.7.0"
DATA_CATALOG_URL = f"https://data-catalog.wildfire.mint.isi.edu"


def getLocalName(id):
    return id.replace("https://w3id.org/okn/i/mint/", "")
