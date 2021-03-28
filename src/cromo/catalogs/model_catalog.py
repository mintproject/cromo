
from modelcatalog.api.dataset_specification_api import DatasetSpecificationApi
from modelcatalog import api_client, configuration
from modelcatalog.api.model_configuration_api import ModelConfigurationApi
from modelcatalog.api.model_configuration_setup_api import ModelConfigurationSetupApi
from modelcatalog.api.variable_presentation_api import VariablePresentationApi
from modelcatalog.api.dataset_specification_api import DatasetSpecificationApi
from modelcatalog.exceptions import ApiException
from cromo.constants import MODEL_CATALOG_URL, DEFAULT_USERNAME, getLocalName

MC_API_CLIENT=api_client.ApiClient(configuration.Configuration(host=MODEL_CATALOG_URL))

# Get all model configurations
def getAllModelConfigurations():
    try:
        # List all Model entities
        api_instance = ModelConfigurationApi(api_client=MC_API_CLIENT)
        configs = api_instance.modelconfigurations_get(username=DEFAULT_USERNAME)
        return configs
    except ApiException as e:
        print("Exception when calling ModelConfigurationApi->modelconfigurations_get: %s\n" % e)
    return []

# create an instance of the API class
def getModelConfigurationDetails(config):
    try:
        spec_api = DatasetSpecificationApi(api_client=MC_API_CLIENT)
        pres_api = VariablePresentationApi(api_client=MC_API_CLIENT)
        if config.has_input is not None:
            new_inputs = []
            for input in config.has_input:
                new_input = spec_api.datasetspecifications_id_get(getLocalName(input.id), username=DEFAULT_USERNAME)
                if new_input.has_presentation is not None:
                    new_presentations = []
                    for pres in new_input.has_presentation:
                        if pres.id is not None:
                            new_presentation = pres_api.variablepresentations_id_get(getLocalName(pres.id), username=DEFAULT_USERNAME)
                            new_presentations.append(new_presentation)
                    new_input.has_presentation = new_presentations
                new_inputs.append(new_input)
            config.has_input = new_inputs
        return config
    except ApiException as e:
        print("Exception when getting model configuration details({}): {}\n".format(config.id, e))
    return None

# Get all model configuration setups
def getAllModelConfigurationSetups():
    try:
        # List all Model entities
        api_instance = ModelConfigurationSetupApi(api_client=MC_API_CLIENT)
        configs = api_instance.modelconfigurationsetups_get(username=DEFAULT_USERNAME)
        return configs
    except ApiException as e:
        print("Exception when calling ModelConfigurationApi->modelconfigurations_get: %s\n" % e)
    return []