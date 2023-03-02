#!/usr/bin/env python

#
# Deploy a package to a single named endpoint or multiple endpoints identified by a question
#

import requests


class TaniumSession(requests.Session):

    '''
    This class is a wrapper for the requests.Session object to handle authentication  

    For more information about the Tanium REST API, please contact your local TAM.
    To use the Tanium API-Gateway, please visit:  https://docs.tanium.com/api_gateway/api_gateway/overview.html

    '''

    # Session object for Tanium API
    def __init__(self, base_url, api_key, timeout=60, completion_percentage=100, verify=True, *args, **kwargs):
        self._base_url = base_url
        self._api_key = api_key
        print("TaniumSession# Base URL: {}".format(self._base_url))   
        print("TaniumSession# API Key: {}".format(self._api_key))
        self._timeout = timeout
        self._completion_percentage = completion_percentage / 100

        # Set the headers for the session
        headers = {
            'Content-Type': 'application/json',
            'session': api_key
        }

        # Initialize the session
        super(TaniumSession, self).__init__(*args, **kwargs)
        self.headers.update(headers)
        self.verify = verify
    # End __init__

    def request(self, method, url, **kwargs):
        """ Automatically attempt to get a new token for authentication errors """

        # If the url is not a full url, then prepend the base url
        resp = super(TaniumSession, self).request(method, url, **kwargs)

        # If the response is a 403 or 401, then refresh the session id and retry
        if resp.status_code in [403, 401]:
            print("Refreshing the session id to retry")

            # Refresh the session id and retry
            self.authenticate(self._username, self._password)
            resp = super(TaniumSession, self).request(method, url, **kwargs)

        return resp
    # End request



