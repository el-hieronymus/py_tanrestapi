import tanRESTsession
from tanRESToutput import TanOutput




class TanEnforce(tanRESTsession.TaniumSession):

    # Class variables
    ENFORCE_PLUGIN_URL = "/plugin/products/enforce"
    ENFORCEMENT_ID = "{}/v1/enforcements/{{id}}/details".format(ENFORCE_PLUGIN_URL)
    ENFORCE_MODULE_INFO = "{}/private/info".format(ENFORCE_PLUGIN_URL)
    ENFORCEMENTS = "{}/v1/enforcements".format(ENFORCE_PLUGIN_URL)


    def __init__(self, baseurl, api_key, verify=True, timeout=60):
        super().__init__(baseurl, api_key, verify, timeout)
    # End __init__

    def get_enforce_policy_enforcement_details(self, policy_id, output="console", wait_time=30):
        
        endpoint = "{}{}".format(self._base_url, self.ENFORCEMENT_ID.format(id=policy_id))

        stream_output = TanOutput(self._base_url, self._api_key, self.verify, wait_time)
        stream_output.output(endpoint, output)
    # End get_enforce_policy_enforcement_details

    def get_enforce_module_info(self, output="console", wait_time=30):
        
        endpoint = "{}{}".format(self._base_url, self.ENFORCE_MODULE_INFO)

        stream_output = TanOutput(self._base_url, self._api_key, self.verify, wait_time)
        stream_output.output(endpoint, output)
    # End get_enforce_module_info

    def get_enforce_enforcements(self, output="console", wait_time=30):
        
        endpoint = "{}{}".format(self._base_url, self.ENFORCEMENTS)

        stream_output = TanOutput(self._base_url, self._api_key, self.verify, wait_time)
        stream_output.output(endpoint, output)
    