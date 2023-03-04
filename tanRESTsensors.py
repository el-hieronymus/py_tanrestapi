import tanRESTsession
import json
import datetime


'''
This class is for the Tanium REST API sensors handling.
For more information about the Tanium REST API, please contact your local TAM.
To use the Tanium API-Gateway, please visit:  https://docs.tanium.com/api_gateway/api_gateway/overview.html
'''
class TanSensors(tanRESTsession.TaniumSession):
    # Class variables
    SENSOR_BY_NAME_ENDPOINT = "/api/v2/sensors/by-name/{sensor_name}"
    # End class variables
    
    def __init__(self, baseurl, api_key, verify=True):
        super().__init__(baseurl, api_key, verify)
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

def _stream_sensor_results(self, action_id, verify_group):
        """ Stream sensor results to console """
        endpoint = "{}{}".format(self._base_url, self.ACTION_RESULTS_ENDPOINT).format(
            action_id=action_id)
        response = self.get(endpoint)
        response.raise_for_status()
        response_json = response.json()
        
        if response_json["data"]["status"] == "complete":
            print("Action completed")
            if verify_group:
                print("Verify group results:")
                print(json.dumps(response_json["data"]["verify_group_results"], indent=2))
            print("Target group results:")
            print(json.dumps(response_json["data"]["target_group_results"], indent=2))
        else:
            print("Action not yet complete")
    # End _stream_sensor_results

if __name__ == "__main__":
    print("This is a library of classes and methods for the Tanium REST API.")