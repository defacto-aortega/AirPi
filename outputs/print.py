import output
import datetime


class Print(output.Output):

    def __init__(self,data):
        pass

    def output_data(self, data_points):
        print ""
        print "Time: " + str(datetime.datetime.now())
        for i in data_points:
            print i["name"] + ": " + str(i["value"]) + " " + i["symbol"]
        return True
