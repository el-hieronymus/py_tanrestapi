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

def _get_config_from_args():
    """ Get the command line arguments """
    parser = argparse.ArgumentParser(description="Tanium REST API Configuration")
    parser.add_argument("-c", "--config_file", help="Path to config file", default=None, required=False)
    parser.add_argument("-o", "--output", help="Style of response output: console or file", default="console", required=False)
    parser.add_argument("-t", "--task", help="Task definition to run either action or sensor",  required=True)
    parser.add_argument("-i", "--info", help="Print this help info", default=None, required=False)

    args = parser.parse_args()
    print ("args: {}".format(args))
    config_from_args = {"config_file":args.config_file, "output":args.output, "task":args.task, "help":args.info}

    return config_from_args
# End get_config_from_args

def _get_config(config_list=None):
    """ Get the configuration """
    json_config = {}

    if config_list["help"] is True:
        _print_help()
        exit()

    # Use the default configuration file if none is specified
    if config_list is None:
        config_list = {"config_file":None, "output":None}

    # If a configuration file is specified, use it
    if config_list["config_file"] is not None and os.path.isfile(config_list["config_file"]):
        print("Using configuration file: {}".format(config_list["config_file"] ))
        json_config = TanGetConfig(config_list["config_file"]).get_config()
    else:
    # Otherwise, return an error
        print("Error: Configuration file not found or invalid JSON")
    
    # If an output file is specified, use it
    if config_list["output"] is not None:
        print("Using output file: {}".format(config_list["output"]))
        json_config.update({"output":config_list["output"]})
    # Otherwise output to console
    else:
        print("Using default output to console")
        json_config.update({"output":"console"})
    
    # Check if Action-Task is question or action:
    if config_list["task"] == "sensor":
        json_config.update({"sensor":True})
    elif config_list["task"] == "action":
        json_config.update({"action":True})
    else:
        print("Error: Please specify either question or action")
        return

    if json_config == {}:
        print("Error: Configuration file not found or invalid JSON")
        return

    return json_config
# End get_config

def _print_header():
    print("Tanium REST API Script")
    print("copyright 2023, Tanium, Inc., andy.elmaghraby@tanium.com")
    print("This script is an example of how to use the Tanium REST API to deploy a package to a single endpoint or a group of endpoints.")
    print("")
    _print_help()
    print("")
# End print_header

def _print_help():
    print("Usage: tanRESTmain.py  -t, --task [-c, --config_file <path to config file>] [-o, --output <console or file>]")
    print("")
    print("Options:")
    print("  -t, --task <question or action>  Specify the task to run. Either question or action")
    print("  -c, --config_file <path to config file>  Specify the path to the configuration file")
    print("  -o, --output <console or file>  Specify the output style. Either console or file")
    print("  -i, --info  Show this help message and exit")
    print("")
    print("Examples:")
    print("Example: tanRESTmain.py  --task question --config_file ./question_conf.json --output result.json")
    print("Example: tanRESTmain.py  -t action -c ./action_conf.json -o console")
    print("")
# End print_help
        
        

def main():
    """ Main function """
    # Write an Intro for the use of the Tanium REST API script:
    _print_header()  

    # Get the command line arguments
    if _get_config_from_args():
        config = _get_config(_get_config_from_args()) 
    else:
        config = _get_config()
    
    if config is None:
        return
    
    print("Config: {}".format(config))
     
    # Disable SSL certificate verification if noverify is set
    if config["noverify"]:
        print("Insecure Warning: Certificate Verification Disabled. Further warnings suppressed.")  
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)    

    if not (config["target"] or config["target_question"]):
        """ Confirm either a single computer name or a targeting question was used """
        raise ValueError("Error: You must specify either a target or a target-question.")
        


    if config["action"]:
        # Create the TaniumSession object
        actions = TanActions(config["base_url"], config["api_key"], not config["noverify"])
        
        # Deploy the package
        if config["target"]:
            single_action = {"action_group":config["action_group"], "target":config["target"], "package":config["package"], "parameters":config["parameters"] }
            actions.deploy_action_single_endpoint(single_action, config["output"])
        else:
            group_action = {"action_group":config["action_group"], "target_question":config["target_question"], "package":config["package"], "parameters":config["parameters"]}
            actions.deploy_action_multiple_endpoints(group_action, config["output"])
    
    elif config["sensor"]:
        # Create the TaniumSession object
        call_question = TanSensors(config["base_url"], config["api_key"], not config["noverify"])

        default_wait_time = 30

        # Get the resulting data for a question
        call_question.get_question_data(
            config["question"],
            config["output"],
            config.get("wait_time", default_wait_time)
        )
# End main()

if __name__ == "__main__":
    main()

# End main