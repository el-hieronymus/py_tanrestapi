import json
import tanRESTsession


class TanSensors(tanRESTsession.TaniumSession):
    BASE_URL = "http://www.coperavia.com:8001/api/v2"
    QUESTION_ENDPOINT = "/questions"
    RESULT_INFO_ENDPOINT = "/result_info/question"

    def __init__(self, baseurl, api_key, verify=True, timeout=60):
        super().__init__(baseurl, api_key, verify, timeout)
    # End __init__

    def _get_question_id(self, json_data):
        response = self.session.post(self.BASE_URL + self.QUESTION_ENDPOINT, json=json_data)
        response.raise_for_status()
        question_id = response.json()["id"]
        return question_id

    def _parse_question(self, question):
        json_data = {
            "question_text": question,
            "parameters": []
        }
        question_id = self._get_question_id(json_data)
        return question_id

    def _output(self, session_id, output):
        response = self.session.get(self.BASE_URL + self.RESULT_INFO_ENDPOINT + f"/{session_id}")
        response.raise_for_status()
        result_data = response.json()
        
        if output == "console":
            self._stream_sensor_results(result_data)
        elif output == "json":
            with open('result_data.json', 'w') as outfile:
                json.dump(result_data, outfile, indent=2)
        else:
            print("Error: Invalid output type")

    def _stream_sensor_results(self, result_data):
        columns = result_data["columns"]
        rows = result_data["rows"]

        for row in rows:
            data = row["data"]
            result = {columns[i]["name"]: data[i][0]["text"] for i in range(len(columns))}
            print(result)

    def run_sensor_query(self, question, output="console"):
        session_id = self._parse_question(question)
        self._output(session_id, output)

def main():
    sensors = TanSensors(TanSensors.BASE_URL, "1234567890")
    sensors.run_sensor_query("Get Computer Name from all machines")

if __name__ == "__main__":
    main()
