

from tanRESTsession import TaniumSession
import json
import time
import datetime

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
    def __init__(self, baseurl, api_key, verify=True, timeout=120):
        # Call the parent constructor
        super().__init__(baseurl, api_key, verify, timeout)

    # Deploy a package to a list of endpoints

    def deploy_action_multiple_endpoints(self, group_action_params, output):

        # Get the parameters
        action_group_name = group_action_params["action_group"]
        package_name = group_action_params["package"]
        parameters = group_action_params["parameters"]
        targeting_question = group_action_params["target_question"]

        # Get the action group id
        action_group_id = self._get_action_group_id(action_group_name)
        if not action_group_id:
            return RuntimeError("Action group {} not found".format(action_group_name))

        # Get the package details
        package_details = self._get_package_details(package_name)
        if not package_details:
            return RuntimeError("Package {} not found".format(package_name))

        # Build the action parameters
        action_params = self._build_action_parameters(
            package_details, parameters)


        # Create the anonymous group
        targeting_group_id = self._create_anonymous_group(targeting_question)

        # json data object for deployment
        data = {
            "action_group": {"id": action_group_id},
            "name": "TestDeploy%s" % package_name,
            "target_group": {
                "and_flag": False,
                "deleted_flag": False,
                "filter_flag": False,
                "management_rights_flag": False,
                "not_flag": False,
                "id": targeting_group_id
            },
            "package_spec": {
                "source_id": package_details["id"],
                "parameters": action_params
            },
            "expire_seconds": 43200,
            "issue_seconds": 0
        }

        # POST request to deploy the package
        try:
            response = self.post("{}{}".format(
                self._base_url, self.ACTIONS_ENDPOINT), json=data)
            response.raise_for_status()
        except Exception as e:
            print("Could not deploy package to endpoints. \n Error: {}".format(e))
            return

        # forward to output:
        self._output(output, response)
        # End deploy_action_multiple_endpoints

    # Deploy a package to a single endpoint
    def deploy_action_single_endpoint(self, action_group_params, output):

        # Get the parameters
        action_group_name = action_group_params["action_group"]
        package_name = action_group_params["package"]
        parameters = action_group_params["parameters"]
        computer_name = action_group_params["target"]

        # get action group ID and package details
        action_group_id = self._get_action_group_id(action_group_name)
        package_details = self._get_package_details(package_name)
        if not package_details:
            return
        action_params = self._build_action_parameters(
            package_details, parameters)
        if action_params == None:
            return

        # get sensor data for "Computer Name"
        sensor_data = self._get_sensor_data("Computer Name")
        sensor_hash = sensor_data["hash"]
        sensor_id = sensor_data["id"]

        # json data object for deployment
        data = {
            "action_group": {"id": action_group_id},
            "name": "TestDeploy%s" % package_name,
            "target_group": {
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
            "package_spec": {
                "source_id": package_details["id"],
                "parameters": action_params
            },
            "expire_seconds": 43200,
            "issue_seconds": 0
        }

        # POST request to deploy package
        try:
            response = self.post("{}{}".format(
                self._base_url, self.ACTIONS_ENDPOINT), json=data)
            response.raise_for_status()
        except:
            print("Error: Could not deploy package to endpoint")
            return

        # forward to output:
        self._output(output, response, package_details)
    # End deploy_action_single_endpoint

    def _get_action_group_id(self, action_group_name):
        resp = self.get("{}{}".format(
            self._base_url, self.ACTION_GROUPS_ENDPOINT))
        resp.raise_for_status()
        action_group_id = None
        for action_group in resp.json()["data"]:
            if action_group["name"] == action_group_name:
                action_group_id = action_group["id"]
                break
        else:
            raise ("Error: Action Group '%s' not found" % action_group_name)

        return action_group_id
    # End _get_action_group_id

    def _create_anonymous_group(self, targeting_question):
        data = {"text": targeting_question}

        resp = self.post("{}{}".format(
            self._base_url, self.GROUPS_ENDPOINT), json=data)
        if resp.status_code == 400:
            print(json.dumps(resp.json(), indent=2))
        resp.raise_for_status()

        return resp.json()["data"]["id"]
    # End _create_anonymous_group

    def _stream_action_results(self, action_id):
        """ poll for updated results for an action id """
        evaluated = 0
        finished = 0
        start_time = time.time()
        end_time = start_time + self._timeout

        resp = self.get("{}{}".format(self._base_url, self.RESULTS_ENDPOINT.format(id=action_id)))
        resp.raise_for_status()
        result = resp.json().get("data", {}).get("result_sets", [])[0]

        # # Print the results in a table
        from prettytable import PrettyTable
        table = PrettyTable()
        #table.field_names = ["Computer Name", "Status", "Count"]
        table.field_names = [column["name"] for column in result.get("columns", [])]

        # Find the index of the "Action Statuses" column
        if result.get("columns"):
            for index, item in enumerate(result.get("columns", [])):
                if item["name"] == "Action Statuses":
                    action_status_index = index
                    break
            else: raise ("Error: Action Statuses field not found in result columns!")

        stars = ["*"]

        # Determine what percentage of endpoints have finished with the action
        while (evaluated < self._completion_percentage or finished < 100.0) and time.time() < end_time:
            # Get the results
            resp = self.get("{}{}".format(
                self._base_url, self.RESULTS_ENDPOINT.format(id=action_id)))
            resp.raise_for_status()
            result = resp.json().get("data", {}).get("result_sets", [])[0]

            # Determine what percentage of endpoints have finished with the action
            action_statuses = [row["data"][action_status_index][0]["text"]
                               for row in result.get("rows", [])]

            # Determine what percentage of endpoints have been evaluated
            evaluated_statuses = ["Expired", "Stopped", "Failed", "Verified", "NotSucceeded", "Completed"]
            total_evaluated_endpoints = len(   [action_status for action_status in action_statuses if action_status in evaluated_statuses]) 
            row_count = len(result.get("rows", []))
            evaluated = 0 if not row_count else float(total_evaluated_endpoints) / float(row_count) * 100.0

            # Print the results in a table
            for row in result.get("rows", []):               
                # TODO: Check is values in row with 
                # "table.add_row([", ".join([value["text"] for value in column]) for column in row["data"]])"
                # is already in the table, if so, skip it:

                for row in table.rows:
                    print ("row: %s" % row)
                    values = [value["text"] for value in row["data"]]
                    if values not in table.rows:
                        table.add_row([", ".join([value["text"] for value in column]) for column in row["data"]])

            table.align = "c"
            print("\033c")
            print(table)
            print("")
            print("Collecting data from %d endpoints" % row_count)
            print("Percentage of endpoints evaluated: %2f%%" % evaluated)
            print("Percentage of endpoints finished with action: %2f%%" % finished)
            print("Time elapsed: %d seconds" % (time.time() - start_time))
            print("Time remaining: %d seconds" % (end_time - time.time()))
            print("")
            
            #append a start ("*") to the stars list and print it:
            stars.append("*")
            print("".join(stars))

            print("Please wait...")

            time.sleep(0.5)
    # End _stream_action_results

    def _get_package_details(self, package_name):
        """ Get the package details """
        endpoint = "{}{}".format(
            self._base_url, self.PACKAGES_ENDPOINT).format(package=package_name)
        response = self.get(endpoint)
        response.raise_for_status()

        resp_data = response.json().get("data")

        if not resp_data:
            print("No package exists with name {} or your account has insufficient permissions to access the packages".format(
                package_name))
            return None

        else:
            return resp_data
    # End _get_package_details

    def _build_action_parameters(self, package_details, parameters):
        #package_id = package_details.get("id")
        #expire_seconds = package_details.get("expire_seconds")
        parameter_definition = package_details.get("parameter_definition")
        formatted_parameters = []
        if parameter_definition:
            parameter_definition = json.loads(parameter_definition)
            required_parameters = parameter_definition["parameters"]

            # compare number of parameters provided to number of required parameters:
            # if they are not equal, return None
            # if they are equal, build the parameters
            if parameters == None:
                print("Please provide %d required package parameters" %
                      len(required_parameters))
                return None
            else:
                parameters = parameters.split(",")

            if len(parameters) != len(required_parameters)+1:
                print("Please provide %d required package parameters" %
                      len(required_parameters))
                return None

            for parameter in parameter_definition["parameters"]:
                try:
                    index = int(parameter["key"][1:]) - 1
                except:
                    print(
                        "Parameter definitions has key in unexpected format: " + parameter.get("key"))
                value = parameters[index]
                formatted_parameters.append({"key": parameter["key"],
                                             "value": value})
        return formatted_parameters
    # End _build_action_parameters

    def _get_action_results(self, action_id):
        pass
    # End _get_action_results

    # output results to json file
    def _stream_action_results_into_json(self, action_id, output_file):
        """ poll for updated results for an action id """
        evaluated = 0
        finished = 0
        start_time = time.time()
        end_time = start_time + self._timeout

        resp = self.get("{}{}".format(self._base_url, self.RESULTS_ENDPOINT.format(id=action_id)))
        resp.raise_for_status()
        result = resp.json().get("data", {}).get("result_sets", [])[0]

        

        # Find the index of the "Action Statuses" column
        if result.get("columns"):
            for index, item in enumerate(result.get("columns", [])):
                if item["name"] == "Action Statuses":
                    action_status_index = index
                    break
            else: raise ("Error: Action Statuses field not found in result columns!")

        stars = ["*", "*",]

        while (evaluated < self._completion_percentage or finished < 100.0) and time.time() < end_time:
            # Get the results
            resp = self.get("{}{}".format(
                self._base_url, self.RESULTS_ENDPOINT.format(id=action_id)))
            resp.raise_for_status()
            result = resp.json().get("data", {}).get("result_sets", [])[0]

            # Determine what percentage of endpoints have finished with the action
            action_statuses = [row["data"][action_status_index][0]["text"]
                               for row in result.get("rows", [])]

            # Determine what percentage of endpoints have been evaluated
            evaluated_statuses = ["Expired", "Stopped", "Failed", "Verified", "NotSucceeded", "Completed"]
            total_evaluated_endpoints = len(   [action_status for action_status in action_statuses if action_status in evaluated_statuses]) 
            row_count = len(result.get("rows", []))
            evaluated = 0 if not row_count else float(total_evaluated_endpoints) / float(row_count) * 100.0
            print("\033c")
            print("Collecting data from %d endpoints" % row_count)
            print("Percentage of endpoints evaluated: %2f%%" % evaluated)
            print("Percentage of endpoints finished with action: %2f%%" % finished)
            print("Time elapsed: %d seconds" % (time.time() - start_time))
            print("Time remaining: %d seconds" % (end_time - time.time()))
            print("")
            
            #append a start ("*") to the stars list and print it:
            stars.append("*")
            print("".join(stars))

            print("Please wait...")


           
            time.sleep(5)
        # write json data to file
        print("Writing results to file: %s" % output_file)
        with open(output_file, 'w') as outfile:
            json.dump(result, outfile, indent=2)    
    # End _stream_action_results_into_json

    def _output(self, output, response):
            # print response and store action ID
        print(json.dumps(response.json(), indent=2))
        action_id = response.json()["data"]["id"]

        if output == "console":
            # stream results to console
            self._stream_action_results(action_id)

        else: 
            # write json data to file
            self._stream_action_results_into_json(action_id, output)

    # End _output