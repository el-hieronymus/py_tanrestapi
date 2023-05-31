import tanRESTsession
from tanRESToutput import TanOutput




class TanEnforce(tanRESTsession.TaniumSession):

    # Class variables
    ENFORCEMENT_ID = "/v1/enforcements/{id}/details"


    def __init__(self, baseurl, api_key, verify=True, timeout=60):
        super().__init__(baseurl, api_key, verify, timeout)
    # End __init__

    def get_enforce_policy_enforcement_details(self, policy_id, output="console", wait_time=30):
        
        endpoint = "{}{}".format(self._base_url, self.ENFORCEMENT_ID.format(id=policy_id))

        stream_output = TanOutput(self._base_url, self._api_key, self.verify, self._timeout)
        stream_output.output(endpoint, output)


