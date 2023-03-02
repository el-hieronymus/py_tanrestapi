import tanRESTsession

'''
This class is for the Tanium REST API sensors handling.
For more information about the Tanium REST API, please contact your local TAM.
To use the Tanium API-Gateway, please visit:  https://docs.tanium.com/api_gateway/api_gateway/overview.html
'''
class TanRESTsensors(tanRESTsession.TaniumSession):
    # Class variables
    SENSOR_BY_NAME_ENDPOINT = "/api/v2/sensors/by-name/{sensor_name}"
    # End class variables
    
    def __init__(self, baseurl, apikey, verify=True):
        super().__init__(baseurl, apikey, verify)


    def _get_sensor_data(self, sensor_name):
        """ Get the definition for a sensor """
        endpoint =  "{}{}".format(self._base_url, self.SENSOR_BY_NAME_ENDPOINT).format(sensor_name=sensor_name)
        response = self.get(endpoint)
        response.raise_for_status()
        return response.json()["data"]
    # End _get_sensor_data



