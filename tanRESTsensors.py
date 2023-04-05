import tanRESTsession
import json
import datetime
import time
import sys
import os



'''
This class is for the Tanium REST API sensors handling.
For more information about the Tanium REST API, please contact your local TAM.
To use the Tanium API-Gateway, please visit:  https://docs.tanium.com/api_gateway/api_gateway/overview.html
'''
class TanSensors(tanRESTsession.TaniumSession):
    # Class variables
    SENSOR_BY_NAME_ENDPOINT = "/api/v2/sensors/by-name/{sensor_name}"
    # End class variables
    
    def __init__(self, baseurl, api_key, verify=True, timeout=60):
        super().__init__(baseurl, api_key, verify, timeout)
    # End __init__


    def _get_sensor_data(self, sensor_name, **kwargs):
        """ Get the definition for a sensor """
        endpoint =  "{}{}".format(self._base_url, self.SENSOR_BY_NAME_ENDPOINT).format(sensor_name=sensor_name)
        response = self.get(endpoint)
        response.raise_for_status()
        return _output(response, **kwargs)
    # End _get_sensor_data

def _output(self, output, response, package_details):
    
        # print response and store action ID
        print(json.dumps(response.json(), indent=2))
        action_id = response.json()["data"]["id"]

        if output == "console":
            # stream results to console
            self._stream_sensor_results(
                action_id, package_details["verify_group"]["id"] != 0)
        elif output == "json":
            # write json data to file
            with open('deploy_action_{}.json'.format(datetime.datetime), 'w') as outfile:
                json.dump(response.json(), outfile, indent=2)
        else:
            print("Error: Invalid output type")
            return
    # End _output

def _stream_sensor_results(self, sessionid):
        """ Stream results from a sensor to the console """
        endpoint = "{}{}".format(self._base_url, self.SENSOR_RESULTS_ENDPOINT).format(
            sessionid=sessionid)
        response = self.get(endpoint, stream=True)
        response.raise_for_status()

        # With PrettyTable print results to console
        from prettytable import PrettyTable
        table = PrettyTable(["Computer Name", "Computer ID", "Sensor Name", "Sensor ID", "Sensor Status", "Sensor Result"])
        table.align["Computer Name"] = "l"
        table.align["Sensor Name"] = "l"
        table.align["Sensor Result"] = "l"

        # Loop through the results
        for line in response.iter_lines():
            if line:
                # Convert the line to a json object
                result = json.loads(line.decode('utf-8'))

                # Print the results to the console
                table.add_row([result["computer_name"], result["computer_id"], result["sensor_name"], result["sensor_id"], result["status"], result["result"]])
                print(table)
                table.clear_rows()

                # If the status is not "in progress", then exit the loop
                if result["status"] != "in progress":
                    break
        

    # End _stream_sensor_results

if __name__ == "__main__":
    print("This is a library of classes and methods for the Tanium REST API.")