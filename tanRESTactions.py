

from tanRESTsession import TaniumSession
import json
import time

'''
This class is for the Tanium REST API actions handling.
For more information about the Tanium REST API, please contact your local TAM.
To use the Tanium API-Gateway, please visit:  https://docs.tanium.com/api_gateway/api_gateway/overview.html
'''
class TanActions(TaniumSession):

    # Class variables
    ACTIONS_ENDPOINT = "/api/v2/actions/"
    ACTION_BY_NAME_ENDPOINT = "/api/v2/actions/by-name/{action_name}"
    RESULTS_ENDPOINT = "/api/v2/result_data/action/{id}"
    ACTION_GROUPS_ENDPOINT = "/api/v2/action_groups/"
    GROUPS_ENDPOINT = "/api/v2/groups/"
    SENSOR_BY_NAME_ENDPOINT = "/api/v2/sensors/by-name/{sensor_name}"
    PACKAGES_ENDPOINT = "/api/v2/packages/by-name/{package}"
    # End class variables

    # Constructor
    def __init__(self, baseurl, api_key, verify=True):
        # Call the parent constructor
        super().__init__(baseurl, api_key, verify)

    # Deploy a package to a list of endpoints
    def deploy_action_multiple_endpoints(self, action_group_name, targeting_question, package_name, parameters):

        # Get the action group id
        action_group_id = self._get_action_group_id(action_group_name)
        if not action_group_id:
            return RuntimeError("Action group {} not found".format(action_group_name))
        
        # Get the package details
        package_details = self._get_package_details(package_name)
        if not package_details:
            return RuntimeError("Package {} not found".format(package_name))
        
        # Build the action parameters
        action_params = self._build_action_parameters(package_details, parameters)
        if not action_params:
            return RuntimeError("Action parameters {} not found".format(parameters))

        # Create the anonymous group
        targeting_group_id = self._create_anonymous_group(targeting_question)

        # json data object for deployment
        data = {
            "action_group": {"id": action_group_id},
            "name":"TestDeploy%s" % package_name,
            "target_group":{
                "and_flag": False,
                "deleted_flag": False,
                "filter_flag": False,
                "management_rights_flag": False,
                "not_flag": False,
                "id": targeting_group_id
            },
            "package_spec" : {
                "source_id" : package_details["id"],
                "parameters": action_params
            },
            "expire_seconds":43200,
            "issue_seconds":0
        }

        # POST request to deploy the package
        try:
            response = self.post("{}{}".format(self._base_url, self.ACTIONS_ENDPOINT), json=data)
            response.raise_for_status()
        except Exception as e:
            print("Could not deploy package to endpoints. \n Error: {}".format(e))
            return

        # Print the response and store the action ID
        print(json.dumps(response.json(), indent=2))
        action_id =  response.json()["data"]["id"]

        # Stream results if verify group is not 0
        self._stream_action_results(action_id, package_details["verify_group"]["id"] != 0)
    # End deply_action_multiple_endpoints

    # Deploy a package to a single endpoint    
    def deploy_action_single_endpoint(self, action_group_name, computer_name, package_name, parameters):
    
        '''
        def deploy_action_single_endpoint

        This function deploys a package to a single endpoint. It takes four parameters: action_group_name,
        computer_name, package_name and parameters. It first gets the action group ID and the package details
        associated with the package name. It then builds the action parameters based on the package details
        and parameters. It then gets sensor data for "Computer Name" and uses it to build a data object
        containing the necessary information for deployment. The data object is then used in a POST request
        to deploy the package, and if successful, it prints out the response from the request and stores
        the action ID for streaming results. Finally, if verify group is not 0, it streams results using the
        action ID and verify group ID.

        Deploy a package to a single endpoint

        Parameters:
            action_group_name (str): The name of the action group to use for the deployment
            computer_name (str): The name of the endpoint to deploy to
            package_name (str): The name of the package to deploy
            parameters (dict): The parameters to use for the package deployment
        Returns:
            dict: The deployment results
        Raises:
            RuntimeError: If the action group, package, or parameters are not found
        '''

        # get action group ID and package details
        action_group_id = self._get_action_group_id(action_group_name)
        package_details = self._get_package_details(package_name)
        if not package_details:
            return
        action_params = self._build_action_parameters(package_details, parameters)
        if action_params == None:
            return

        # get sensor data for "Computer Name"
        sensor_data = self._get_sensor_data("Computer Name")
        sensor_hash = sensor_data["hash"]
        sensor_id = sensor_data["id"]

        # json data object for deployment
        data = {
            "action_group": {"id": action_group_id},
            "name":"TestDeploy%s" % package_name,
            "target_group":{
                "and_flag": False,
                "deleted_flag": False,
                "filter_flag": False,
                "filters": [],
                "management_rights_flag": False,
                "not_flag": False,
                "sub_groups": [
                    {
                        "and_flag": True,
                        "deleted_flag": False,
                        "filter_flag": False,
                        "filters": [
                            {
                                "all_times_flag": False,
                                "all_values_flag": False,
                                "delimiter": "",
                                "delimiter_index": 0,
                                "ignore_case_flag": True,
                                "max_age_seconds": 0,
                                "not_flag": False,
                                "operator": "Equal",
                                "sensor": {
                                    "hash": sensor_hash,
                                    "id": sensor_id,
                                    "name": "Computer Name"
                                },
                                "substring_flag": False,
                                "substring_length": 0,
                                "substring_start": 0,
                                "utf8_flag": False,
                                "value": computer_name,
                                "value_type": "String"
                            }
                        ],
                        "management_rights_flag": False,
                        "not_flag": False,
                        "sub_groups": []
                    }
                ]
            },
            "package_spec" : {
                "source_id" : package_details["id"],
                "parameters": action_params
            },
            "expire_seconds":43200,
            "issue_seconds":0
        }

        # POST request to deploy package
        try:
            response = self.post("{}{}".format(self._base_url, self.ACTIONS_ENDPOINT), json=data)
            response.raise_for_status()
        except:
            print("Error: Could not deploy package to endpoint")
            return

        # print response and store action ID
        print(json.dumps(response.json(), indent=2))
        action_id =  response.json()["data"]["id"]

        # stream results
        self._stream_action_results(action_id, package_details["verify_group"]["id"] != 0)
    # End deploy_action_single_endpoint

    def _get_action_group_id(self, action_group_name):
        resp = self.get("{}{}".format(self._base_url, self.ACTION_GROUPS_ENDPOINT))
        resp.raise_for_status()
        action_group_id = None
        for action_group in resp.json()["data"]:
            if action_group["name"] == action_group_name:
                action_group_id = action_group["id"]
                break
        else:
            raise("Error: Action Group '%s' not found" % action_group_name)

        return action_group_id
    #End _get_action_group_id

    def _create_anonymous_group(self, targeting_question):
        data = {"text": targeting_question}

        resp = self.post("{}{}".format(self._base_url, self.GROUPS_ENDPOINT), json=data)
        if resp.status_code == 400:
            print(json.dumps(resp.json(), indent=2))
        resp.raise_for_status()

        return resp.json()["data"]["id"]
    # End _create_anonymous_group

    def _stream_action_results(self, action_id, package_verification=False):
        """ poll for updated results for an action id """
        evaluated = 0
        finished = 0
        end_time = time.time() + self._timeout
        rows_printed = 0
        action_status_index = None

        while (evaluated < self._completion_percentage or finished < 100.0) and time.time() < end_time:
            resp = self.get("{}{}".format(self._base_url, self.RESULTS_ENDPOINT.format(id=action_id)))
            resp.raise_for_status()
            result = resp.json().get("data", {}).get("result_sets", [])[0]
            mr_tested = result.get("mr_tested")
            estimated_total = result.get("estimated_total")
            if mr_tested and estimated_total:
                # Determine what percentage of the endpoints have evaluated whether to run the action
                evaluated = float(mr_tested) / float(estimated_total)
            if result.get("columns") and action_status_index == None:
                # Find the index of the "Action Statuses" column
                for index, item in enumerate(result.get("columns", [])):
                    if item["name"] == "Action Statuses":
                        action_status_index = index
                        break
                else:
                    raise("Error: Action Statuses field not found in result columns!")


            # Determine what percentage of endpoints have finished with the action
            action_statuses = [row["data"][action_status_index][0]["text"] for row in result.get("rows", [])]

            finished_statuses = ["Expired", "Stopped", "Failed", "Verified", "NotSucceeded"]
            unfinished_statuses = ["PendingVerification", "Running", "Downloading", "Copying", "Waiting"]
            if package_verification:
                unfinished_statuses.append("Completed")
            else:
                finished_statuses.append("Completed")

            total_completed_endpoints = sum([sum([state in action_status for action_status in action_statuses]) for state in finished_statuses])
            #total_completed_endpoints = sum([action_statuses.count(state) for state in finished_statuses])
            row_count = len(result.get("rows", []))
            finished = 0 if not row_count else float(total_completed_endpoints) / float(row_count) * 100.0
            print("Estimated %2f%% of %d endpoints finished with action" % (finished, row_count))

            for row in result.get("rows", []):
                print(' | '.join([", ".join([value["text"] for value in column]).ljust(25, ' ') for column in row["data"]]))
            time.sleep(5)
    # End _stream_action_results

    def _get_package_details(self, package_name):
        """ Get the package details """
        endpoint =  "{}{}".format(self._base_url, self.PACKAGES_ENDPOINT).format(package=package_name)
        response = self.get(endpoint)
        response.raise_for_status()

        resp_data = response.json().get("data")

        if not resp_data:
            print("No package exists with name {} or your account has insufficient permissions to access the packages".format(package_name))
            return None

        else:
            return resp_data
    # End _get_package_details

    def _build_action_parameters(self, package_details, parameters):
        package_id = package_details.get("id")
        expire_seconds = package_details.get("expire_seconds")
        parameter_definition = package_details.get("parameter_definition")
        formatted_parameters = []
        if parameter_definition:
            parameter_definition = json.loads(parameter_definition)
            required_parameters = parameter_definition["parameters"]
            if len(parameters) != len(required_parameters):
                print("Please provide %d required package parameters" % len(required_parameters))
                return None

            for parameter in parameter_definition["parameters"]:
                try:
                    index = int(parameter["key"][1:]) - 1
                except:
                    print("Parameter definiton has key in unexpected format: " + parameter.get("key"))
                value = parameters[index]
                formatted_parameters.append({"key": parameter["key"],
                                             "value": value })
        return formatted_parameters
    # End _build_action_parameters    

    def _get_action_results(self, action_id):
        pass
    # End _get_action_results