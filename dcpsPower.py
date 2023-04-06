# import minimalmodbus
# import numpy as np


def f32_decode(result):
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, Endian.Big, wordorder=Endian.Little)
    return decoder.decode_32bit_float()

class dcpsPower:
    def __init__(self, client, unit=1):
        self.unit = unit
        self.client = client

    def setValue(self, value):
        print(f"Type B setting value: {value}")
 
    def getOutputVoltage(self):
        address = 0x0B00
        voltage = self.client.read_register(address=address, count=2, slave=self.unit)
        print(f32_decode(voltage))
        return voltage

    def setOutputVoltage(self, voltage):
        address = 0x0A05
        voltage = self.client.write_register(address=address, value=voltage) #, salve=self.unit)

        return True

    def getMaxVoltage(self):
        address = 0x0A01
        voltage = self.client.read_register(address=address, count=2, slave=self.unit)
        print(f32_decode(voltage))
        return voltage

    def getOutputCurrent(self):
        address = 0x0B02
        voltage = self.client.read_register(address=address, count=2, slave=self.unit)
        print(f32_decode(voltage))
        return voltage

    def setOutputCurrent(self, current):
        address = 0x0A07
        voltage = self.client.write_register(address=address, value=current, slave=self.unit)

        return True

    def getMaxCurrent(self):
        address = 0x0A03
        voltage = self.client.read_register(address=address, count=2, slave=self.unit)
        print(f32_decode(voltage))
        return voltage

    def getRemoteStatus(self):
        status = None
        address = 0x0500
        status = self.client.read_coils(address=address, count=1, slave=self.unit)
        return status.bits[0]
    
    def setRemoteStatus(self):
        address = 0x0500
        value = 1
        self.client.write_coil(address=address, value=value, slave=self.unit)

        # return self.write_coil(int('0x0500', 1)
    def setStart(self):
        """set PSU to start."""
        address = 0x0A00
        value = 3 # ramp up
        self.write_register(address=address, value=value, slave=self.unit)
        value = 6 # open output, maybe not need?
        self.write_register(address=address, value=value, slave=self.unit)        
 
    def setStop(self):
        """set PSU to stop"""
        address = 0x0A00
        value = 7 # close output
        self.write_register(address=address, value=value, slave=self.unit)

if __name__ == '__main__':
    from dcpsPower import dcpsPower
    import time
    from pymodbus.client import ModbusSerialClient
    from pymodbus.exceptions import ModbusIOException

    # Define the Sorensen DLM600-5Em9E RS232 serial connection parameters
    baudrate = 9600
    bytesize = 8
    parity = 'N'
    stopbits = 1
    timeout = 0.1
    port = 'COM5'  # Replace with your own serial port name
    
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
    aa = client.connect()
    if aa:
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