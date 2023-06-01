'''
Module Name: tanRESTsensors.py
Description: This module is for the Tanium REST API sensors handling.
For more information about the Tanium REST API, please contact your local TAM.
To use the Tanium API-Gateway, please visit:  https://docs.tanium.com/api_gateway/api_gateway/overview.html

Author: Andy El Maghraby
Date: 2023-05-31

'''
import tanRESTsession
import time
import json
import os
from prettytable import PrettyTable




class TanSensors(tanRESTsession.TaniumSession):
    # Class variables
    SENSOR_BY_NAME_ENDPOINT = "/api/v2/sensors/by-name/{sensor_name}"
    PARSE_QUESTION = "/api/v2/parse_question"
    QUESTIONS = "/api/v2/questions"
    RESULT_DATA = "/api/v2/result_data/question/{session_id}?json_pretty_print=1"
    RESULT_INFO = "/api/v2/result_info/question/{session_id}?json_pretty_print=1"
    # End class variables
    
    def __init__(self, baseurl, api_key, verify=True, timeout=60):
        super().__init__(baseurl, api_key, verify, timeout)
    # End __init__


    def get_question_data(self, question, output="console", wait_time=30):
        """ Get the result data for a question """
        response = self._parse_question(question)
        #get key '0' from 'data' key in response-dictionary:
        json_data = response['data'][0]

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


    def _stream_sensor_results(self, session_id):
            """ Stream results from a sensor to the console """

            # Initialize PrettyTable
            table = PrettyTable()

            # Set table formatting options
            table.header_style = "upper"
            table.border = True
            table.valign = "m"
            table.padding_width = 10
            table.align = "l"

            # Start time
            start_time = time.time()

            # Maximum wait time in seconds
            max_wait_time = 30

            # Stars to print while waiting for the question to complete
            stars = ["*"]

            # List to store the latest 10 rows
            latest_rows = []
            print_latest_rows = True
            number_of_rows_to_keep = 10

            # Continuously poll the sensor results
            while True:
                # Get the current results
                endpoint = "{}{}".format(self._base_url, self.RESULT_DATA).format(session_id=session_id)

                response = self.get(endpoint)
                json_response = response.json().get('data').get('result_sets')[0]
                #print ("JSON Response: {}".format(json_response))

                ep_tested = json_response.get('tested')
                estimated_total = json_response.get('estimated_total')
                print("Row Count: {}".format(ep_tested))
                print("Estimated Total: {}".format(estimated_total))

                # Check if there are results
                if ep_tested != 0 and ep_tested is not None: 
                    # Clear the table
                    table.clear_rows()

                    # Get the columns from the first result
                    columns = json_response.get('columns')
                    column_names = [column.get('name') for column in columns]
                    table.field_names = column_names

                    # Loop through the rows
                    for row in json_response.get('rows'):
                        # Get the data from the row
                        row_data = [item[0].get('text') for item in row.get('data')]
                        table.add_row(row_data)
                        
                        # Add the row to the latest rows list
                        latest_rows.append(row_data)
                        # Trim the list to keep only the latest rows
                        if len(latest_rows) > number_of_rows_to_keep:
                            latest_rows.pop(0)


                    # Set table alignment
                    for field_name in column_names:
                        table.align[field_name] = "l"

                    # Check if the latest rows should be printed
                    if print_latest_rows is True:
                        # Print the table with the latest 10 rows
                        table.clear_rows()
                        for row in latest_rows:
                            table.add_row(row)

                    # Clear the console screen
                    os.system('cls' if os.name == 'nt' else 'clear')
                    # Print the table
                    print(table)
                    table.clear_rows()

                # Check if the row_count of question is > 90% of estimated_total then break 
                if ep_tested >= estimated_total * 0.9:
                    print("Question complete > 90 percent of estimated_total")
                    break

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
    # End _stream_sensor_results

if __name__ == "__main__":
    print("This is a library of classes and methods to request sensor questions for the Tanium REST API.")

