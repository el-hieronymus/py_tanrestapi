import json

'''
Class TanGetConfig is for reading the configuration file for the Tanium REST API.
'''
class TanGetConfig:
    # Class variables
    CONFIG_FILE = "tanRESTconf.json"
    # End class variables

    def __init__(self, config_file=None):
        self._config = {}
        if config_file is not None:
            print("TanGetConfig# Using configuration file: {}".format(config_file))
            self._config_file = config_file
        else:
            print("TanGetConfig# Using default configuration file: {}".format(self.CONFIG_FILE))
            self._config_file = self.CONFIG_FILE
        self._config = self._read_config_file()
    # End __init__

    def _read_config_file(self):
        """ Read the configuration file """
        try:
            with open(self._config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("TanGetConfig# Configuration file not found")
            return {}
        except json.JSONDecodeError:
            print("TanGetConfig# Configuration file is not valid JSON")
            return {}
    # End _read_config_file

    def get_config(self):
        """ Return the configuration """
        return self._config
    # End get_config

    def get_api_key(self):
        """ Return the API key """
        print("TanGetConfig# API key: {}".format(self._config.get("api_key")) )
        return self._config.get("api_key")
    # End get_api_key

    def get_base_url(self):
        """ Return the base URL """
        return self._config.get("base_url")
    # End get_base_url

    def get_target(self):
        """ Return the target """
        print("TanGetConfig# Target: {}".format(self._config.get("target")))  
        return self._config.get("target")
    # End get_target

    def get_target_question(self):
        """ Return the target question """
        print("Target question: {}".format(self._config.get("target_question")))
        return self._config.get("target_question")
    # End get_target_question

    def get_action_group(self):
        """ Return the action group """
        return self._config.get("action_group")
    # End get_action_group

    def get_package(self):
        """ Return the package """
        return self._config.get("package")
    
    def get_noverify(self):
        """ Return the noverify """
        return self._config.get("noverify")
    
    def get_parameters(self):
        """ Return the parameters """
        return self._config.get("parameters")
    # End get_package
