# import minimalmodbus
# import numpy as np

class ka3005pPower:
    def __init__(self, client, unit=1):
        self.unit = unit
        self.client = client

    def getOutputVoltage(self):
        voltage = self.client.query('VOUT1?')
        return voltage

    def setOutputVoltage(self, voltage):
        self.client.write('VSET1:%4.3f' % (voltage))
        return True

    def getMaxVoltage(self):
        pass
        return True

    def getOutputCurrent(self):
        current = self.client.query('IOUT1?')
        return current

    def setOutputCurrent(self, current):
        self.client.write('ISET1:%4.3f' % (current))
        return True

    def getMaxCurrent(self):
        pass
        return True

    def getRemoteStatus(self):
        pass
        return True
    
    def setRemoteStatus(self):
        pass
        return True
    
    def setStart(self):
        self.client.write('OVP1')
        # time.sleep(0.1)
        self.client.write('OCP1')
        # time.sleep(0.1)
        self.client.write('OUT1')

        return True
    
    def setStop(self):
        # self.write('OUT1')
        self.client.write('VSET1:0') ## have to use 0v to stop? bug?
        return True

if __name__ == '__main__':
    from ka3005pPower import ka3005pPower
    import time
    
    import pyvisa
    rm = pyvisa.ResourceManager()
    # rm.list_resources()
    client = rm.open_resource('ASRL3::INSTR')
    # print(inst.query("*IDN?"))

    power = ka3005pPower(client)

    power.setOutputVoltage(0.0)
    power.setOutputCurrent(1.0)
    power.setStart()
    print("start")
    for i in range(0,4):
        power.setOutputVoltage(i)
        time.sleep(5)
        print(i)
    # power.setOutputCurrent(1.0)


    power.setOutputVoltage(0.0)
    client.close()