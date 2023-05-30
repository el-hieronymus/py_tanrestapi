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
    RESULT_DATA = "/api/v2/result_info/question/{session_id}?json_pretty_print=1"
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
        json_data = self._parse_question(question)
        session_id = self._get_question_id(json_data)
        self._output(session_id, output)
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


    def _output(self, session_id, output ):
        """ store session ID and path to output """

        if output == "console":
            # Stream results to console
            self._stream_sensor_results(session_id)

        elif output == "json":

            time.sleep(20.0) # Wait for the question to run

             # Get the current results
            endpoint = "{}{}".format(self._base_url, self.RESULT_DATA.format(session_id=session_id) )

            response = self.get(endpoint)
            # Convert the response to JSON
            json_data = response.json()

            # Write json data to file
            with open('response.json', 'w') as outfile:
                json.dump(json_data, outfile, indent=4)

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

    def _stream_sensor_results_OLD(self, session_id):
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
            endpoint = "{}{}".format(self._base_url, self.RESULT_DATA).format(session_id=session_id)

            response = self.get(endpoint)
            json_response = response.json()

            # Check if there are results
            if 'rows' in json_response:
                # Clear the table
                table.clear_rows()

                # Get the columns from the first result
                columns = json_response['columns']
                column_names = [column['name'] for column in columns]
                table.field_names = column_names

                # Loop through the rows
                for row in json_response['rows']:
                    row_data = [item['text'] for item in row['data']]
                    table.add_row(row_data)

                # Print the table
                print(table)

            # Check if the question is complete
            if json_response.get('complete', False):
                print("Question complete")
                break
            else:
                # Append a star ("*") to the stars list and print it
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

