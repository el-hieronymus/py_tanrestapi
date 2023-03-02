'''

This script is an example of how to use the Tanium REST API to deploy a package to a
single endpoint or a group of endpoints.
Use of the config.json file is optional. If you do not use the config.json file, you
will be prompted for the API key.

// Information for the use of json config file for Tanium API calls
// Please enter your configuration information below
// - API key  (required)
// - Base URL (required)
// - Target is the computer or single endpoint
// - Target Question is the Tanium Interact question to target a group of endpoints
// - Action Group is the Tanium Computer Group to target

// SAMPLE USAGE:

// -noverify
// -baseurl https://taniumserver/
// -action-group "All Computers" 
// -package "Custom Tagging - Add Tags" testtag
// Group of endpoints:
// -target-question "Custom Tag Exists[TestTag,1] matches true" 
// Single endpoint:
// -target "DELL-PC-3002" 
'''
#!/usr/bin/env python3

import urllib3
import argparse
import getpass
import os
from tanRESTsession import TaniumSession
from tanRESTgetconfig import TanGetConfig
from tanRESTactions import TanActions

# Class variables
CONFIG_FILE = "taas_conf.json"
# End class variables

def get_config_from_args():
    """ Get the command line arguments """
    parser = argparse.ArgumentParser(description="Tanium REST API Configuration")
    parser.add_argument("-config_file", help="Path to config file")
   
    return parser.parse_args().config_file
# End get_args

def get_config(config_file=None):
    """ Get the configuration """
    if config_file is not None:
        print("Using configuration file: {}".format(config_file))
        json_config = TanGetConfig(config_file).get_config()
    else:
        print("Using default configuration file: {}".format(CONFIG_FILE))
        json_config = TanGetConfig(CONFIG_FILE).get_config()

    if json_config == {}:
        print("Error: Configuration file not found or invalid JSON")
        return

    return json_config
# End get_config

def main():
    """ Main function """

    # Get the command line arguments
    if get_config_from_args():
        config = get_config(get_config_from_args()) 
    else:
        config = get_config()   
    
    # Disable SSL certificate verification if noverify is set
    if config["noverify"]:
        print("Insecure Warning: Certificate Verification Disabled. Further warnings suppressed.")  
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)    

    if not (config["target"] or config["target_question"]):
        raise ValueError("Must specify target")
        # Confirm either a single computer name or a targeting question was used
        print("Error: Please specify either target or target-question.")
        return

    # Create the TaniumSession object
    actions = TanActions(config["base_url"], config["api_key"], config["noverify"])
    
    if config["target"]:
        actions.deploy_action_single_endpoint(config["action_group"], config["target"], config["package"], config["parameters"])
    else:
        actions.deploy_action_multiple_endpoints(config["action_group"], config["target_question"], config["package"], config["parameters"])

if __name__ == "__main__":
    main()

