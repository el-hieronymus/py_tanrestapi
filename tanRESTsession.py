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
    def __init__(self, base_url, api_key, verify=True, timeout=120, completion_percentage=100, username=None, password=None, *args, **kwargs):
        self._base_url = base_url
        self._api_key = api_key
        self._username = username
        self._password = password
        self._retry = 0

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
        super().__init__(*args, **kwargs)
        self.headers.update(headers)
        self.verify = verify
    # End __init__

    def request(self, method, url, **kwargs):
        """ Automatically attempt to get a new token for authentication errors """

        # If the url is not a full url, then prepend the base url
        resp = super(TaniumSession, self).request(method, url, **kwargs)
        print("TaniumSession# Request: {} {}".format(method, url))
        print("TaniumSession# Response: {}".format(resp.status_code))

        # If the response is a 403 or 401, then refresh the session id and retry
        if resp.status_code in [403, 401] and self._retry < 2:
            print("Refreshing the session id to retry")
            self._retry += 1
            # Refresh the session id and retry
            
            import getpass
            self._username = input("Username: ")
            self._password = getpass.getpass("Password: ")
            
            self.authenticate(self._username, self._password)
            resp = super(TaniumSession, self).request(method, url, **kwargs)
            
        elif resp.status_code is 200:
            return resp
        
        else:
            print("TaniumSession# Response: {}".format(resp.json()))
        
        raise(resp.raise_for_status() if resp.status_code != 200 else "Unable to authenticate")
        exit()
        
    # End request

    def authenticate(self, username, password):
        """ Authenticate to the Tanium server """

        self._username = username
        self._password = password

        # Set the headers for the session
        headers = {
            'Content-Type': 'application/json',
            'session': self._api_key
        }

        # Set the authentication parameters
        params = {
            'username': username,
            'password': password
        }

        # Authenticate to the Tanium server
        resp = self.post(self._base_url + '/session', json=params, headers=headers)

        # If the response is a 200, then set the session id
        if resp.status_code == 200:
            print("Authentication successful")
            self._api_key = resp.json()['session']
            self.headers.update({'session': self._api_key})
        else:
            print("Authentication failed")
            print("Response: {}".format(resp.json()))
        # End if



