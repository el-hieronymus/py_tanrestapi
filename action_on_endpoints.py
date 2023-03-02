#!/usr/bin/env python

#
# Deploy a package to a single named endpoint or multiple endpoints identified by a question
#

"""
SAMPLE USAGE:

python3 action_on_endpoints.py --noverify --baseurl https://192.168.1.200/ --target-question "Custom Tag Exists[TestTag,1] matches true" --action-group "All Computers" --package "Custom Tagging - Add Tags" testtag

python3 action_on_endpoints.py --noverify --baseurl https://192.168.1.200/ --target "DESKTOP-C4QORAO" --action-group "All Computers" --package "Custom Tagging - Add Tags" testtag
token-d4a2a8ccd8b078a250689741b52d2311c4aad61b99e1b076174f20f304
"""

import argparse
import getpass
import json
import time
import requests
import urllib3


class TaniumSession(requests.Session):
    PACKAGES_ENDPOINT = "/api/v2/packages/by-name/{package}"
    ACTIONS_ENDPOINT = "/api/v2/actions"
    SENSOR_BY_NAME_ENDPOINT = "/api/v2/sensors/by-name/{sensor_name}"
    RESULTS_ENDPOINT = "/api/v2/result_data/action/{id}"
    GROUPS_ENDPOINT = "/api/v2/groups"
    ACTION_GROUPS_ENDPOINT = "/api/v2/action_groups"

    def __init__(self, base_url, api_key, timeout=60, completion_percentage=100, verify=True, *args, **kwargs):
        self._base_url = base_url
        self._api_key = api_key
        self._timeout = timeout
        self._completion_percentage = completion_percentage / 100

        headers = {
            'Content-Type': 'application/json',
            'session': api_key
        }
        super(TaniumSession, self).__init__(*args, **kwargs)
        self.headers.update(headers)
        self.verify = verify
    # End __init__

    def request(self, method, url, **kwargs):
        """ Automatically attempt to get a new token for authentication errors """

        resp = super(TaniumSession, self).request(method, url, **kwargs)

        if resp.status_code in [403, 401]:
            print("Refreshing the session id to retry")
            self.authenticate(self._username, self._password)
            resp = super(TaniumSession, self).request(method, url, **kwargs)

        return resp
    # End request

    def deploy_action_multiple_endpoints(self, action_group_name, targeting_question, package_name, parameters):
        """ Deploy a package to a list of endpoints """
        action_group_id = self._get_action_group_id(action_group_name)
        package_details = self._get_package_details(package_name)
        if not package_details:
            return
        action_params = self._build_action_parameters(package_details, parameters)
        #if action_params == None:
        #    return

        targeting_group_id = self._create_anonymous_group(targeting_question)

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

        response = self.post("{}{}".format(self._base_url, self.ACTIONS_ENDPOINT), json=data)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))

        action_id =  response.json()["data"]["id"]
        self._stream_action_results(action_id, package_details["verify_group"]["id"] != 0)
    # End deploy_action_multiple_endpoints

    def deploy_action_single_endpoint(self, action_group_name, computer_name, package_name, parameters):
        """ Deploy a package to a single endpoint """
        action_group_id = self._get_action_group_id(action_group_name)
        package_details = self._get_package_details(package_name)
        if not package_details:
            return
        action_params = self._build_action_parameters(package_details, parameters)
        if action_params == None:
            return

        sensor_data = self._get_sensor_data("Computer Name")
        sensor_hash = sensor_data["hash"]
        sensor_id = sensor_data["id"]

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

        response = self.post("{}{}".format(self._base_url, self.ACTIONS_ENDPOINT), json=data)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))

        action_id =  response.json()["data"]["id"]
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

    def _get_sensor_data(self, sensor_name):
        """ Get the definition for a sensor """
        endpoint =  "{}{}".format(self._base_url, self.SENSOR_BY_NAME_ENDPOINT).format(sensor_name=sensor_name)
        response = self.get(endpoint)
        response.raise_for_status()
        return response.json()["data"]
    # End _get_sensor_data

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


def main():
    parser = argparse.ArgumentParser(description="ask a Tanium question")
    parser.add_argument("--noverify", help="don't verify ssl cert (self-signed)", action="store_true")
    parser.add_argument("--target")
    parser.add_argument("--target-question")
    parser.add_argument("--action-group", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("parameters", nargs="*")
    parser.add_argument("--baseurl", required=True)
    parser.add_argument("--apikey")
    args = parser.parse_args()

    apikey = args.apikey or getpass.getpass("Tanium API Key: ")

    if args.noverify:
        print("Insecure Warning: Certificate Verification Disabled. Further warnings suppressed")
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if not bool(args.target) ^ bool(args.target_question):
        # Confirm either a single computer name or a targeting question was used
        print("Specify either target or target-question")
        return

    session = TaniumSession(args.baseurl, apikey, verify=not(args.noverify))
    if args.target:
        session.deploy_action_single_endpoint(args.action_group, args.target, args.package, args.parameters)
    else:
        session.deploy_action_multiple_endpoints(args.action_group, args.target_question, args.package, args.parameters)


if __name__ == "__main__":
    main()
