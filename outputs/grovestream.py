import output
import requests
import json


class GroveStream(output.Output):
    requiredOptions = ["api_key", "comp_id"]

    def __init__(self, data):
        self.APIKey = data["api_key"]
        self.CompId = data["comp_id"]

    def output_data(self, data_points):
        arr = []
        for i in data_points:
            arr.append({"compId": self.CompId, "streamId": i["sensor"], "data": i["value"]})
        json_dump = json.dumps(arr)
        try:
            url = "http://grovestreams.com/api/feed?api_key="+self.APIKey
            print url
            response = requests.put(url, headers=None, data=json_dump)
            if response.text != "":
                print "GrooveStream Error: " + response.text
                return False
        except Exception:
            return False
        return True
