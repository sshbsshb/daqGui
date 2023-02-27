#!/usr/bin/python3

import serial

# Assumes the following settings for the DCS M9 RS-232 Interface
# Baud-rate = 19200
# Hardware Flow Control = None

class sorensenPower:
    # DEFAULT_TIMEOUT = 0.125

    # List of commands
    COMMAND_IDN                     = "*IDN?\r"

    COMMAND_MEASURE_CURRENT         = ":MEAS:CURR?\r"
    COMMAND_MEASURE_VOLTAGE         = ":MEAS:VOLT?\r"
    COMMAND_SET_VOLTAGE             = ":SOUR:VOLT {:1.03f}\r"
    COMMAND_SET_VOLTAGE_RAMP        = ":SOUR:VOLT:RAMP {:1.03f} {:1.01f}\r"
    COMMAND_SET_CURRENT             = ":SOUR:CURR {:1.03f}\r"
    COMMAND_GET_STATUS              = ":SOUR:STAT:BLOC?\r"
    COMMAND_RETURN_LOCAL            = ":SYST:LOCAL ON\r"

    def __init__(self, client, debug=False):
        # self.portName = portName
        # self.baudrate = baudrate

        # self.port = serial.Serial()
        # self.port.baudrate = self.baudrate
        # self.port.port = self.portName
        # self.port.timeout = self.DEFAULT_TIMEOUT
        # self.port.rts = True
        # self.port.dtr = True

        self.debug = debug

        self.model = None
        self.serialNumber = None
        self.maxVoltage = None
        self.maxCurrent = None
        self.client = client

        # self.connect()
        self.getModel()

    # def __del__(self):
    #     # Make sure we return control to local.
    #     self.disconnect()

    def _writeCommand(self, command):
        result = None

        # if (self.debug is True):
        #     print(command.encode())
        # try:
        self.client.write(command.encode())
        result = self.client.readline().decode(encoding='UTF-8')
        # except ModbusIOException as e:
        #     print(f"Error reading registers from Sorensen: {e}")
        if (self.debug is True):
            print(command.encode())
            print("> " + result)

        return result

    # def connect(self):
    #     success = False

    #     if (self.port.isOpen() == False):
    #         self.port.open()

    #     self.getStatus()

    #     success = self.port.isOpen()

    #     return success

    # def disconnect(self, returnToLocal=True):
    #     if (returnToLocal == True):
    #         self._writeCommand(self.COMMAND_RETURN_LOCAL)

    #     success = False

    #     if (self.port.isOpen() == True):
    #         self.port.close()
    #         success = True

    #     return success

    def getModel(self, forceUpdate=False):
        if ((self.model is None) or forceUpdate):
            self.getStatus()

        return self.model

    def getSerialNumber(self, forceUpdate=False):
        if ((self.serialNumber is None) or forceUpdate):
            self.getStatus()

        return self.serialNumberequvilent

    def getMaxVoltage(self, forceUpdate=False):
        if ((self.maxVoltage is None) or forceUpdate):
            self.getStatus()

        return self.maxVoltage

    def getMaxCurrent(self, forceUpdate=False):
        if ((self.maxCurrent is None) or forceUpdate):
            self.getStatus()

        return self.maxCurrent

    def getIdentification(self):
        identification = self._writeCommand(self.COMMAND_IDN)
        return identification.strip()

    def getOutputVoltage(self):
        voltageASCII = self._writeCommand(self.COMMAND_MEASURE_VOLTAGE)
        voltage = float(voltageASCII.strip())

        return voltage

    def getOutputCurrent(self):
        currentASCII = self._writeCommand(self.COMMAND_MEASURE_CURRENT)
        current = float(currentASCII.strip())

        return current

    def setOutputVoltage(self, voltage):
        success = False

        if ((voltage >= 0.0) and (voltage <= self.maxVoltage)):
            self._writeCommand(self.COMMAND_SET_VOLTAGE.format(voltage))
            success = True

        return success

    def setOutputVoltageRamp(self, endVoltage, rampTimeSec):
        success = Falseequvilent
        if ((endVoltage >= 0.0) and (endVoltage <= self.maxVoltage) and (rampTimeSec >= 0.0) and (rampTimeSec < 99.0)):
            self._writeCommand(self.COMMAND_SET_VOLTAGE_RAMP.format(endVoltage, rampTimeSec))
            success = True

        return success

    def setOutputCurrent(self, current):
        success = False

        if ((current >= 0) and (current <= self.maxCurrent)):
            self._writeCommand(self.COMMAND_SET_CURRENT.format(current))
            success = True

        return success

    def getStatus(self):
        status = None

        statusASCII = self._writeCommand(self.COMMAND_GET_STATUS).strip().split(',')

        # Doesn't seem to follow the interface spec
        if (len(statusASCII) == 23):
            statusRegister = int(statusASCII[3])
            overTemperature = bool((statusRegister >> 4) & 0x01)
            overVoltage     = bool((statusRegister >> 3) & 0x01)
            constantCurrent = bool((statusRegister >> 1) & 0x01)
            constantVoltage = bool((statusRegister >> 0) & 0x01)

            status = {
                'channelNumber'     : int(statusASCII[0]),
                'onlineStatus'      : int(statusASCII[1]),
                'statusFlags'       : int(statusASCII[2]),
                'statusRegister'    : statusRegister,
                'accumulatedStatus' : int(statusASCII[4]),
                'faultMask'         : int(statusASCII[5]),
                'faultRegister'     : int(statusASCII[6]),
                'errorRegister'     : int(statusASCII[7]),
                'overTemperature'   : overTemperature,
                'overVoltage'       : overVoltage,
                'constantCurrent'   : constantCurrent,
                'constantVoltage'   : constantVoltage,
                'serialNumber'      : statusASCII[8],
                'voltageCapability' : float(statusASCII[9]),
                'currentCapability' : float(statusASCII[10]),
                'overVoltage'       : float(statusASCII[11]),
                'voltageDacGain'    : float(statusASCII[12]),
                'voltageDacOffset'  : float(statusASCII[13]),
                'currentDacGain'    : float(statusASCII[14]),
                'currentDacOffset'  : float(statusASCII[15]),
                'protectionDacGain' : float(statusASCII[16]),
                'protectionDacOffset': float(statusASCII[17]),
                'voltageAdcGain'    : float(statusASCII[18]),
                'voltageAdcOffset'  : float(statusASCII[19]),
                'currentAdcGain'    : float(statusASCII[20]),
                'currentAcOffset'   : float(statusASCII[21]),
                'model'             : statusASCII[22]
            }

            self.model = status['model']
            self.serialNumber = status['serialNumber']
            self.maxCurrent = status['currentCapability']
            self.maxVoltage = status['voltageCapability']

        return status


if __name__ == '__main__':

    import sorensenPower, time
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

        power = sorensenPower(client)
        # Define the Sorensen DLM600-5Em9E Modbus slave ID
        slave_id = 1

        print("Model: {}".format(power.getModel()))
        print("Serial Number: {}".format(power.getSerialNumber()))

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


        ### testing send string method here

        from pymodbus.client import ModbusSerialClient

        client = ModbusSerialClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600)

        # Connect to the Modbus server
        client.connect()

        # Encode the string as a series of 16-bit Unicode characters
        message = b'\x01\x10\x00\x10\x00\x0C\x18\x24\x3E\x4A\x56\x62\x6E\x7A'

        # Send the message and receive the response
        response = client.send(message)

        # Close the connection
        client.close()