'''

This script is an example of how to use the Tanium REST API to deploy a package to a
single endpoint or a group of endpoints.

'''
#!/usr/bin/env python3

import urllib3
import argparse
import os
from tanRESTgetconfig import TanGetConfig
from tanRESTactions import TanActions
from tanRESTsensors import TanSensors

# Class variables
CONFIG_FILE = "taas_conf.json"
# End class variables

def get_config_from_args():
    """ Get the command line arguments """
    parser = argparse.ArgumentParser(description="Tanium REST API Configuration")
    parser.add_argument("-config_file", help="Path to config file", default=None)
    parser.add_argument("-output", help="Style of response output: console or file", default="console")
    parser.add_argument("question", help="Option to run question", default=None, nargs="?", const="question")
    parser.add_argument("action", help="Option to run action", default=None, nargs="?", const="action")

    return {"config_file":parser.parse_args().config_file, "output":parser.parse_args().output, "question":parser.parse_args().question, "action":parser.parse_args().action}
# End get_config_from_args

def get_config(config_files=None):
    """ Get the configuration """
    json_config = {}

    # Use the default configuration file if none is specified
    if config_files is None:
        config_files = {"config_file":None, "output":None}

    # If a configuration file is specified, use it
    if config_files["config_file"] is not None and os.path.isfile(config_files["config_file"]):
        print("Using configuration file: {}".format(config_files["config_file"] ))
        json_config = TanGetConfig(config_files["config_file"]).get_config()
    else:
    # Otherwise, return an error
        print("Error: Configuration file not found or invalid JSON")
    
    # If an output file is specified, use it
    if config_files["output"] is not None and os.path.isfile(config_files["output"]):
        print("Using output file: {}".format(config_files["output"]))
        json_config.update({"output":config_files["output"]})
    # Otherwise output to console
    else:
        print("Using default output to console")
        json_config.update({"output":"console"})
    
    # Check if Action is sensor or action:
    if config_files["question"] is not None:
        json_config.update({"question":True})
    elif config_files["action"] is not None:
        json_config.update({"action":True})
    else:
        print("Error: Please specify either question or action")
        return

    if json_config == {}:
        print("Error: Configuration file not found or invalid JSON")
        return

    return json_config
# End get_config

def main():
    """ Main function """
    # Write an Intro for the use of the Tanium REST API script:
    print("Tanium REST API Script")
    print("This script is an example of how to use the Tanium REST API to deploy a package to a single endpoint or a group of endpoints.")
    print("")
    print("Usage: tanRESTmain.py [-config_file <path to config file>] [-output <console or file>] <sensor or package> <package name>")
    print("Example: tanRESTmain.py -config_file ./question_conf.json -output result.json question")
    print("Example: tanRESTmain.py -config_file ./action_conf.json -output console action")
    

    # Get the command line arguments
    if get_config_from_args():
        config = get_config(get_config_from_args()) 
    else:
        config = get_config()
    
    if config is None:
        return
    
    # Disable SSL certificate verification if noverify is set
    if config["noverify"]:
        print("Insecure Warning: Certificate Verification Disabled. Further warnings suppressed.")  
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)    

    if not (config["target"] or config["target_question"]):
        raise ValueError("Must specify target")
        # Confirm either a single computer name or a targeting question was used
        print("Error: Please specify either target or target-question.")
        return

    if config["package"]:
        # Create the TaniumSession object
        actions = TanActions(config["base_url"], config["api_key"], not config["noverify"])
        
        # Deploy the package
        if config["target"]:
            single_action = {"action_group":config["action_group"], "target":config["target"], "package":config["package"], "parameters":config["parameters"] }
            actions.deploy_action_single_endpoint(single_action, config["output"])
        else:
            group_action = {"action_group":config["action_group"], "target_question":config["target_question"], "package":config["package"], "parameters":config["parameters"]}
            actions.deploy_action_multiple_endpoints(group_action, config["output"])
    
    elif config["question"]:
        # Create the TaniumSession object
        ask_question = TanSensors(config["base_url"], config["api_key"], not config["noverify"])
        ask_question.get_sensor_data(config["question"], config["output"])
        # Run the question
        
           



if __name__ == "__main__":
    main()

# End main