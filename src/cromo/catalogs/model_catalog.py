import re
import json
import copy
import itertools
from modelcatalog import api_client, configuration
from modelcatalog.api.model_configuration_api import ModelConfigurationApi
from modelcatalog.api.model_configuration_setup_api import ModelConfigurationSetupApi
from modelcatalog.exceptions import ApiException
from cromo.catalogs.data_catalog import getMatchingDatasetResources, getMatchingDatasets 
from cromo.constants import EXECUTION_ONTOLOGY_URL, MODEL_CATALOG_URL, DEFAULT_USERNAME, ONTOLOGY_DIR, RULES_DIR, getLocalName
from owlready2 import onto_path, get_ontology, Imp, sync_reasoner_pellet

from cromo.metadata.sensors import SENSORS

MC_API_CLIENT=api_client.ApiClient(configuration.Configuration(host=MODEL_CATALOG_URL))

onto_path.append(ONTOLOGY_DIR)

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

# Get all model configuration setups
def getAllModelConfigurationSetups():
    try:
        # List all Model entities
        api_instance = ModelConfigurationSetupApi(api_client=MC_API_CLIENT)
        configs = api_instance.modelconfigurationsetups_get(username=DEFAULT_USERNAME)
        return configs
    except ApiException as e:
        print("Exception when calling ModelConfigurationApi->modelconfigurationsetups_get: %s\n" % e)
    return []


# Get Input details of a model configuration (or a setup)
def getModelConfigurationDetails(config_id):
    try:
        api_instance = ModelConfigurationSetupApi(api_client=MC_API_CLIENT)
        config = api_instance.custom_modelconfigurationsetups_id_get(getLocalName(config_id), username=DEFAULT_USERNAME)
        return config
    except ApiException as e:
        print("Exception when getting model configuration details({}): {}\n".format(config_id, e))
    return None

# Fetch rules. TODO: Fetch this from the model catalog
def getModelRulesFromFile(configid, rulesdir=RULES_DIR):
    rules = []
    try:
        with open("{}/{}.rules".format(rulesdir, getLocalName(configid))) as fd:
            rulestring = fd.read()
            rules = splitModelRulesString(rulestring)
    except FileNotFoundError as e:
        pass
        #print("Rules file not found for {}: {}".format(configid, e))
    return rules

def getModelRulesFromConfig(config):
    rules = []
    if config.has_constraint is not None:
        for cons in config.has_constraint:
            for rule in cons.has_rule:
                rules.extend(splitModelRulesString(rule))
    return rules

def splitModelRulesString(rules_string):
    rules = []
    currule = ""
    for rule in rules_string.splitlines():
        srule = rule.strip()
        if re.match("^#", srule):
            continue
        if srule == "":
            rules.append(currule)
            currule = ""
        else:
            currule += srule
    if currule.strip() != "":
        rules.append(currule)
    return rules

class ModelRuleInput:
    def __init__(self, input, variable):
        self.input = input
        self.variable = variable


def searchFunctionArguments(fn, rule):
    args = {}
    for item in rule.body:
        if item.property_predicate is not None and item.property_predicate.name == fn:
            if len(item.arguments) == 2:
                if item.arguments[0] not in args:
                    args[item.arguments[0]] = []
                args[item.arguments[0]].append(item.arguments[1])
    return args

def parseModelRule(rule):
    ruleinputs = []
    inputargs = searchFunctionArguments("hasModelInput", rule)
    labelargs = searchFunctionArguments("hasLabel", rule)
    bindingargs = searchFunctionArguments("hasDataBinding", rule)
    varargs = searchFunctionArguments("hasVariable", rule)

    # Get all relevant model inputs in the rule
    for ex,ivars in inputargs.items():
        for ivar in ivars:
            # Get the label of the model inputs
            if ivar in labelargs:
                ivarlabel = labelargs[ivar][0]
                # Get the dataset binding for the model inputs
                if ivar in bindingargs:
                    ibinding = bindingargs[ivar][0]
                    # Check which data variable the rule refers to
                    if ibinding in varargs:
                        for dvar in varargs[ibinding]:
                            if dvar in labelargs:
                                # Get the label of the data variable
                                dvarlabel = labelargs[dvar][0]
                                ruleinputs.append({
                                    "input": ivarlabel,
                                    "variable": dvarlabel
                                })
    return ruleinputs


CACHED_DERIVED_VARIABLES = {}
def getDerivedVariableValues(config, input_type, input_urls, derived_variable, region_geojson, start_date, end_date):
    key = "{}-{}-{}-{}-{}".format(input_urls, derived_variable, region_geojson, start_date, end_date)
    if key in CACHED_DERIVED_VARIABLES:
        return CACHED_DERIVED_VARIABLES[key]

    # TODO: Run code here to generate the derived_variable
    # - Have a mapping for datatype:variable to code
    # - Run the code and return all relevant derived variables
    if derived_variable in SENSORS:
        typefns = SENSORS[derived_variable]
        if input_type in typefns:
            fn = typefns[input_type]
            res = fn(input_urls, region_geojson, start_date, end_date)
            CACHED_DERIVED_VARIABLES[key] = res["values"]
            return res["values"]
    return {}


def runExecutionRules(onto, rules):
    with onto:
        for r in rules:
            rule = Imp()
            rule.set_as_rule(r)


# Check which inputs do we have to process: { i, m } (input and metadata from that input)
# - Get datasets for these inputs : { dj }
# - Run the variable generation code on each of them
#   - Store the list of metadata and values for each dataset djmv = (dj, {m, mv})
# - For each relevant rule input, store a list of { (i, { djmv }) }
# - Create a cross product for all input djmv lists
# - For each item in the cross product
#   - Create a ModelExecution in owlready2 with appropriate values of i, m, mv
#   - Run all model rules ( one by one ?)
#   - Check if the model is valid
def checkConfigViability(configId, region_geojson, start_date, end_date, rulesdir=RULES_DIR, ontdir=ONTOLOGY_DIR):
    print("Get model IO details...", end='\r')
    config = getModelConfigurationDetails(configId)

    # FIXME: Could also return configs without inputs ?
    if config.has_input is None:
        return None

    # FIXME: Change to getModelRules from model catalaog (or config should already have it)
    # rules = getModelRulesFromFile(configId, rulesdir=rulesdir)
    rules = getModelRulesFromConfig(config)

    # FIXME: For now only proceeding if there are rules for this model
    if len(rules) == 0:
        return None

    print("\n{}\n{}".format(config.label[0], "="*len(config.label[0])))

    if ontdir not in onto_path:
        onto_path.append(ontdir)

    relevant_input_variables = {}
    onto = get_ontology(EXECUTION_ONTOLOGY_URL).load()
    with onto:
        for r in rules:
            rule = Imp()
            rule.set_as_rule(r)
            ruleinputs = parseModelRule(rule)
            for rinput in ruleinputs:
                ivar = rinput["input"]
                if ivar not in relevant_input_variables:
                    relevant_input_variables[ivar] = []
                if rinput["variable"] not in relevant_input_variables[ivar]:
                    relevant_input_variables[ivar].append(rinput["variable"])

    print("{}".format(''.join([' ']*100)), end='\r') # Clear line

    input_djmvs = {}

    for input in config.has_input:
        input_label = input.label[0]

        # If this input is used in the rule
        if input_label in relevant_input_variables:
            # Get the variable to derive for this input
            derived_variables = relevant_input_variables[input_label]

            # Fetch dataset information for this input from the data catalog
            if input.has_presentation is not None:
                print("\nInput: {}".format(input_label))
                # Get Variables for this input
                variables = []
                for pres in input.has_presentation:
                    if pres.has_standard_variable is not None:
                        variables.append(pres.has_standard_variable[0].label[0])
                #print("\tVariables: {}".format(str(variables)))

                print(f"- Searching datasets containing variables '{variables}' for this region and time period...", end='\r')
                datasets = getMatchingDatasets(variables, region_geojson, start_date, end_date)
                print("{}".format(''.join([' ']*100)), end='\r') # Clear line

                djmvs = []
                if len(datasets) == 0:
                    print("\r- No datasets found in data catalog matching input variables {} for this region and time period.".format(variables))
                else:
                    # Get datasets that match the input type as well
                    matches = datasets #matchTypedDatasets(datasets, input.type)
                    if len(matches) == 0:
                        print("\r- No datasets found in data catalog for matching type")

                    for ds in matches:
                        meta = ds["dataset_metadata"]
                        print("\r- Dataset: {} ( Fetching files... )".format(ds["dataset_name"]), end='\r')
                        
                        resources = getMatchingDatasetResources(ds["dataset_id"], region_geojson, start_date, end_date)

                        print("\r- Dataset: {} ( {} files... )       ".format(ds["dataset_name"], len(resources)))

                        resource_urls = list(map(lambda res: res["resource_data_url"], resources))

                        if len(resources) == 0:
                            print("- No files found")
                            continue

                        print("\t- Deriving {} values for dataset...".format(str(derived_variables)), end='\r')
                        derived_variable_values = {}
                        for derived_variable in derived_variables:
                            if derived_variable not in derived_variable_values:
                                values = getDerivedVariableValues(config, meta["datatype"], resource_urls, derived_variable, region_geojson, start_date, end_date)
                                derived_variable_values.update(values)

                        for dv,dvv in derived_variable_values.items():
                            print("\t- {} = {}{}".format(dv, dvv, ''.join([' ']*50)))

                        djmvs.append({
                            "dataset": ds,
                            "derived_variables": derived_variable_values
                        })

                input_djmvs[input_label] = djmvs

    # Create Cross product combinations across all input djmvs
    keys = list(input_djmvs.keys())
    values = list(input_djmvs.values())
    products = list(itertools.product(*values))
    input_djmv_combos = []
    for prod in products:
        combo = {}
        for i in range(0, len(keys)):
            combo[keys[i]] = prod[i]
        input_djmv_combos.append(combo)

    if len(input_djmv_combos) > 0:
        print("\nConstraint Reasoning Over MOdel:")

    return_values = []

    # For each combination, create an onto, and run the rules
    # Check if the combination is valid
    count = 1
    for input_djmv_combo in input_djmv_combos:
        print("\n------ Data combination {} -------".format(count))
        count += 1
        for input_label, djmv in input_djmv_combo.items():
            print("- {} : {}".format(input_label, djmv["dataset"]["dataset_name"]))

        return_djmv_combo = []
        onto = get_ontology(EXECUTION_ONTOLOGY_URL).load()
        with onto:
            exobj = onto.ModelExecution()
            exobj.hasModelInput = []
            for r in rules:
                rule = Imp()
                rule.set_as_rule(r)
            for input_label, djmv in input_djmv_combo.items():
                return_djmv = copy.deepcopy(djmv)

                inobj = onto.ModelInput()
                inobj.hasLabel = input_label
                inobj.hasDataBinding = []
                exobj.hasModelInput.append(inobj)
        
                dsobj = onto.DataBinding()
                inobj.hasDataBinding.append(dsobj)
                dsobj.hasVariable = []

                return_derived_variables = []
                for dv,dvv in djmv["derived_variables"].items():
                    dvarobj = onto.Variable()
                    dvarobj.hasLabel = dv
                    dvarobj.hasValue = dvv
                    dsobj.hasVariable.append(dvarobj)
                    return_derived_variables.append({
                        "variable_id": dv,
                        "value": dvv
                    })
                return_djmv["dataset"]["derived_variables"] = return_derived_variables
                return_djmv_combo.append({
                    "input_id": input_label,
                    "dataset": return_djmv["dataset"]
                })
                        
            sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True, debug=0)

            valid = None
            recommended = None            
            for exv in exobj.isValid:
                if exv and valid is None:
                    valid = True
                if not(exv):
                    valid = False
            for exr in exobj.isRecommended:
                if exr and recommended is None:
                    recommended = True
                if not(exr):
                    recommended = False

            print("")
            if recommended == True:
                print("\u2713 RECOMMENDED")
            elif recommended == False:
                print("\u2717 NOT RECOMMENDED") 
            if valid == True:
                print("\u2713 VALID")
            elif valid == False:
                print("\u2717 INVALID") 

            for reason in exobj.hasValidityReason:
                print("\t \u2713 {}".format(reason))
            for reason in exobj.hasInvalidityReason:
                print("\t \u2717 {}".format(reason))
            for reason in exobj.hasRecommendationReason:
                print("\t \u2713 {}".format(reason))
            for reason in exobj.hasNonRecommendationReason:
                print("\t \u2717 {}".format(reason))

            return_values.append({
                "inputs": return_djmv_combo,
                "validity": {
                    "valid": valid,
                    "validity_reasons": exobj.hasValidityReason,
                    "invalidity_reasons": exobj.hasInvalidityReason,
                    "recommended": recommended,
                    "recommendation_reasons": exobj.hasRecommendationReason,
                    "non_recommendation_reasons": exobj.hasNonRecommendationReason                    
                }
            })
            onto.destroy()

    return return_values
