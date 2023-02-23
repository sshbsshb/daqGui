# import minimalmodbus
# import numpy as np



class dcpsPower:
    def __init__(self, client, unit=8):
        self.unit = unit
        self.client = client

    def getOutputVoltage(self):
        voltageASCII = self.read_register(int('0x2101', 16))
        voltage = float(voltageASCII.strip())

        return voltage

    def setOutputVoltage(self, voltage):
        success = False

        if ((voltage >= 0.0) and (voltage <= self.maxVoltage)):
            self._writeCommand(self.COMMAND_SET_VOLTAGE.format(voltage))
            success = True

        return success

    def setOutputCurrent(self, current):
        success = False

        if ((current >= 0) and (current <= self.maxCurrent)):
            self._writeCommand(self.COMMAND_SET_CURRENT.format(current))
            success = True

        return success

    def getOutputCurrent(self):
        currentASCII = self._writeCommand(self.COMMAND_MEASURE_CURRENT)
        current = float(currentASCII.strip())

        return current
    
    def getRemoteStatus(self):
        status = None

        statusASCII = self._writeCommand(self.COMMAND_GET_STATUS).strip().split(',')
        return status
    
    def setRemoteStatus(self):
        success = False

        statusASCII = self._writeCommand(self.COMMAND_GET_STATUS).strip().split(',')
        return success
    
    def set_frequency(self, freq):
        """set frequency, 2 digits"""
        # return self.write_register(int('0x2001', 16),
        #                                       freq, 2, functioncode=6)
        self.np_cmd = [1, int('0x2001', 16), int(freq*100), self.unit]  #1 write, add, number, unit
        self.enqueue(self.np_cmd)  # read True

    def get_frequency(self):
        """get frequency, 2 digits"""
        # return self.read_register(int('0x2102', 16), 2)

        self.np_cmd = [0, int('0x2102', 16), 1, self.unit] #0 read, add, count, unit
        self.enqueue(self.np_cmd) # read True

    def get_status(self):
        """check if motor in operation, 1 for running, 2 digits"""
        # run = self.read_register(int('0x2101', 16))
        # return run & 0b11

        self.np_cmd = [0, int('0x2101', 16), 1, self.unit]  # 0 read, add, count, unit
        self.enqueue(self.np_cmd)  # read True

    def set_start(self):
        """set VFD to start."""
        # return self.write_register(int('0x2000', 16),
        #                                       0b00100010, functioncode=6)

        # self.np_cmd = [1, int('0x2000', 16), 0b00100010, self.unit]  #1 write, add, number, unit---REV, bit 5~4
        self.np_cmd = [1, int('0x2000', 16), 0b00010010, self.unit]  # 1 write, add, number, unit----FWD
        self.enqueue(self.np_cmd)  # read True

    def set_stop(self):
        """set VFD to stop"""
        # return self.write_register(int('0x2000', 16),
        #                                       0b00100001, functioncode=6)

        # self.np_cmd = [1, int('0x2000', 16), 0b00100001, self.unit]  #1 write, add, number, unit---REV, bit 5~4
        self.np_cmd = [1, int('0x2000', 16), 0b00010001, self.unit]  # 1 write, add, number, unit---FWD
        self.enqueue(self.np_cmd)  # read True



if __name__ == '__main__':
    import dcpsPower, time
    from pymodbus.client import ModbusSerialClient
    from pymodbus.exceptions import ModbusIOException

    # Define the Sorensen DLM600-5Em9E RS232 serial connection parameters
    baudrate = 19200
    bytesize = 8
    parity = 'N'
    stopbits = 1
    timeout = 0.1
    port = '/dev/ttyUSB0'  # Replace with your own serial port name
    
    # Create a ModbusSerialClient object for the Sorensen DLM600-5Em9E
    client = ModbusSerialClient(
        method='rtu',
        port=port,
        baudrate=baudrate,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits,
        rtscts=True,
        timeout=timeout
    )
    if client.connect():
        power = dcpsPower(client)

        power.setOutputVoltage(0.0)
        power.setOutputCurrent(5.0)

        print("Ramping from 0.0v to 4.0v over 2 seconds.")
        power.setOutputVoltageRamp(4.0, 2.0)

        end = time.monotonic() + 100

        while (time.monotonic() < end):
            voltage = power.getOutputVoltage()
            current = power.getOutputCurrent()
            if abs(current) < 0.001:
                resistance = 1e10
            else:
                resistance = voltage / current

            print("Voltage: {:1.03f}, Current: {:1.03f}, Resistance: {:1.03f}".format(voltage, current, resistance))

        power.setOutputVoltage(0.0)
        client.close()