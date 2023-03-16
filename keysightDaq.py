import time
import random

class keysightDaq:

    def __init__(self, client, debug=True):
        self.debug = debug

        self.serialNumber = None
        self.client = client

    def setValue(self, value):
        print(f"Type A setting value: {value}")
    
    def restDaq(self):
        self.client.write("*RST")
        time.sleep(0.5)

    def setDaqChannels(self, loaded_setting):

        scan_list = []
        if not self.debug:
            self.restDaq()

            for i, item in enumerate(loaded_setting):
                # print(':CONFigure:%s %s,%s,(@%s)' % (item['Measurement'], item['Probe type'], item['Sensor type'], item['Channel id']))
                self.client.write(':CONFigure:%s %s,%s,(@%s)' % (item['Measurement'], item['Probe type'], item['Sensor type'], item['Channel id']))
                time.sleep(0.1)
                scan_list.append(item['Channel id'])
                # self.updateDisplayData(i, item['Display'])
            time.sleep(0.1)
            scan_list_str = ",".join(str(i) for i in scan_list)
            # print((':ROUTe:SCAN (@%s)' % (scan_list_str)))
            self.client.write(':ROUTe:SCAN (@%s)' % (scan_list_str))
            # sum(list(map(scan_list_str, count_element)))
        else:
            for i, item in enumerate(loaded_setting):
                scan_list.append(item['Channel id'])
            # scan_list_str = ",".join(str(i) for i in scan_list)

        return scan_list

    def getDaqChannels(self):
        if not self.debug:
            # temp_data = []
            # for channel in self.channels:
            #     reading = self.daq.query(f"MEASure:VOLTage:DC? (@{channel})")
            #     temp_data.append(float(reading))
            reading = self.client.query(':READ?')
            # time.sleep(0.5)
            format_values = [float(val) for val in reading.split(",")]
            # self.data_ready.emit(format_values)
        else:
            self.nPlots = 7
            format_values = random.sample(range(101), self.nPlots)

            # Convert the list to a string
            # reading = ', '.join(str(x) for x in my_list)
            # self.data_ready.emit(my_list)
        return format_values
