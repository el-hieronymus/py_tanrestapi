import tanRESTsession
import time
import json
from prettytable import PrettyTable



'''
This class is for the Tanium REST API sensors handling.
For more information about the Tanium REST API, please contact your local TAM.
To use the Tanium API-Gateway, please visit:  https://docs.tanium.com/api_gateway/api_gateway/overview.html
'''
class TanSensors(tanRESTsession.TaniumSession):
    # Class variables
    SENSOR_BY_NAME_ENDPOINT = "/api/v2/sensors/by-name/{sensor_name}"
    PARSE_QUESTION = "/api/v2/parse_question"
    QUESTIONS = "/api/v2/questions"
    RESULT_DATA = "/api/v2/result_data/question/{session_id}?json_pretty_print=1"
    # End class variables
    
    def __init__(self, baseurl, api_key, verify=True, timeout=60):
        super().__init__(baseurl, api_key, verify, timeout)
    # End __init__


    """def get_question_data(self, question, output="console", wait_time=30):
        # Get the result data for a question 
        session_id = self._get_question_id(self._parse_question(question))   # Parse the question and get the session ID
        
        time.sleep(wait_time) # Wait for the question to run

        endpoint = "{}{}".format(self._base_url, self.RESULT_DATA.format(session_id=session_id) )
        try:
            response = self.get(endpoint)
            response.raise_for_status()
            return self._output(response, output)
        except:
            print(Exception, " Error: Could not get the result data for the question in get_result_data()")
            return
    # End get_result_data
    """

    def get_question_data(self, question, output="console", wait_time=30):
        """ Get the result data for a question """
        session_id = self._get_question_id(self._parse_question(question))
        self._stream_sensor_results(session_id)
    # End get_question_data




    def _get_question_id(self, json_data):
        """ Get the session ID for a question """
        endpoint = "{}{}".format(self._base_url, self.QUESTIONS)
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = self.post(endpoint, headers=headers, json=json_data)
            return response.json()['data']['id']
        except:
            print(Exception, "Error: Could not get the result data for the question in question()")
            return
    # End question


    def _parse_question(self, question):
        """ Get the definition for a sensor """
        endpoint =  "{}{}".format(self._base_url, self.PARSE_QUESTION)

        data = {
            "text": question
        }
        try:
            response = self.post(endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except:
            print(Exception, "Error: Could not parse the question text in parse_question()")
            return    
    # End parse_question   


    def _output(self, response, output ):
        """ store session ID and path to output """

        if output == "console":
            # Stream results to console
            self._stream_sensor_results(response)

        elif output == "json":
            # Write json data to file
            with open('response.json', 'w') as outfile:
                json.dump(response, outfile, indent=4)

        else:
            print(Exception, " Error: Invalid output type in _output()")
            return
    # End _output

    """def _stream_sensor_results(self, response):
       # Stream results from a sensor to the console 
       # Initialize PrettyTable
       table = PrettyTable()

       # Check if there are results
       if 'results' in response:
           # Get the keys from the first result to use as the table field names
           table.field_names = response['results'][0].keys()

           # Loop through the results
           for result in response['results']:
               table.add_row(result.values())

       # Print the table
       print(table)
    # End _stream_sensor_results 
    
    """

    def _stream_sensor_results(self, session_id):
        """ Stream results from a sensor to the console """

        # Initialize PrettyTable
        table = PrettyTable()

        # Start time
        start_time = time.time()

        # Maximum wait time in seconds
        max_wait_time = 120

        # Stars to print while waiting for the question to complete
        stars = ["*"]

        # Continuously poll the sensor results
        while True:
            # Get the current results
            endpoint = "{}{}".format(self._base_url, self.RESULT_DATA.format(session_id=session_id) )

            response = self.get(endpoint)
            # Convert the response to JSON
            json_response = response.json()

            # Check if there are results
            if 'results' in json_response:
                # Clear the table
                table.clear_rows()

                # Get the keys from the first result to use as the table field names
                table.field_names = response['results'][0].keys()

                # Loop through the results
                for result in response['results']:
                    table.add_row(result.values())

                # Print the table
                print(table)
            
            # Check if the question is complete
            if json_response.get('question', {}).get('complete') is True:
                print("Question complete")
                break
            else:
                #append a start ("*") to the stars list and print it:
                stars.append("*")
                print("".join(stars))


            # Check if the maximum wait time has been exceeded
            elapsed_time = time.time() - start_time
            if elapsed_time > max_wait_time:
                print("Maximum wait time exceeded. Exiting...")
                break

            # Wait for a bit before polling again
            time.sleep(5)


if __name__ == "__main__":
    print("This is a library of classes and methods to request sensor questions for the Tanium REST API.")

