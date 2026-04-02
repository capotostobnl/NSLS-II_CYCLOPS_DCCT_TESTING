"""This module is for implementing remote control of Rigol DP800 series
power supplies.
This module works for the following models:
DP832(A)
DP831(A)
DP822(A)
DP821(A)
DP813(A)
DP811(A)

M. Capotosto
3/4/2025
NSLS-II Diagnostics and Instrumentation
"""

from time import sleep
from instrument_modules.visa_utils import connect_usb_instrument, \
    connect_ethernet_instrument  # Importing utility module


DELAY = 0.01  # 10ms delay


class DP800:
    """Create PSU Class"""
    # *************************************************************************
    # ******Initialize Connection******
    def __init__(self, connection_method, address):
        if connection_method == "USB":
            self.device, self.address, self.status = \
                connect_usb_instrument(address)
            self.connected_with = 'USB' if self.status == "Connected" else None
        elif connection_method == "IP":
            self.device, self.address, self.status = \
                connect_ethernet_instrument(address)
            self.connected_with = 'Ethernet' \
                if self.status == "Connected" else None

    # *************************************************************************
    # ******Factory Reset******
    def factory_reset(self):
        """define a FACTORY RESET function"""
        command = "*RST"
        self.device.write(command)
        sleep(5)  # 5 second delay to wait for reset to finish...

    # *************************************************************************
    # Output Configuration

    def select_output(self, chan):
        """define a CHANNEL SELECT function"""
        command = f":INST:NSEL {chan}"
        self.device.write(command)
        sleep(DELAY)

    def toggle_output(self, chan, state):
        """Define a TOGGLE OUTPUT function"""
        command = f":OUTP CH{chan},{state}"
        self.device.write(command)
        sleep(DELAY)

    def set_voltage(self, chan, val):
        """define a SET VOLTAGE function"""
        command = f":INST:NSEL {chan}"
        self.device.write(command)
        sleep(DELAY)
        command = f":VOLT {val}"
        self.device.write(command)
        sleep(DELAY)

    def set_current(self, chan, val):
        """define a SET CURRENT function"""
        command = f":INST:NSEL {chan}"
        self.device.write(command)
        sleep(DELAY)
        command = f":CURR {val}"
        self.device.write(command)
        sleep(DELAY)

    def set_ovp(self, chan, val):
        """define a SET VOLT PROTECTION function"""
        command = f":INST:NSEL {chan}"
        self.device.write(command)
        sleep(DELAY)
        command = f":VOLT:PROT {val}"
        self.device.write(command)
        sleep(DELAY)

    def toggle_ovp(self, chan, state):
        """define a TOGGLE VOLTAGE PROTECTION function"""
        command = f":INST:NSEL {chan}"
        self.device.write(command)
        sleep(DELAY)
        command = f"VOLT:PROT:STAT {state}"
        self.device.write(command)
        sleep(DELAY)

    def set_ocp(self, chan, val):
        """define a SET CURRENT PROTECTION function"""
        command = f":INST:NSEL {chan}"
        self.device.write(command)
        sleep(DELAY)
        command = f":CURR:PROT {val}"
        self.device.write(command)
        sleep(DELAY)

    def toggle_ocp(self, chan, state):
        """define a TOGGLE CURRENT PROTECTION function"""
        command = f":INST:NSEL {chan}"
        self.device.write(command)
        sleep(DELAY)
        command = f":CURR:PROT:STAT {state}"
        self.device.write(command)
        sleep(DELAY)

    def measure_voltage(self, chan):
        """define a MEASURE VOLTAGE function"""
        command = f":MEAS:VOLT? CH{chan}"
        volt = self.device.query(command)
        volt = float(volt)
        sleep(DELAY)
        return volt

    def measure_current(self, chan):
        """define a MEASURE CURRENT function"""
        command = f":MEAS:CURR? CH{chan}"
        curr = self.device.query(command)
        curr = float(curr)
        sleep(DELAY)
        return curr

    def measure_power(self, chan):
        """define a MEASURE POWER function"""
        command = f":MEAS:POWE? CH{chan}"
        power = self.device.query(command)
        power = float(power)
        sleep(DELAY)
        return power

    def apply(self, chan, voltage, current):
        """Apply command function for simple voltage/current setting"""
        command = f":APP CH{chan},{voltage},{current}"
        power = self.device.query(command)
        power = float(power)
        sleep(DELAY)

    def psu_test(self):
        """PSU Test"""
        self.set_voltage(chan=2, val=5.0)
        self.set_voltage(chan=3, val=5.0)
        sleep(1)
        self.set_voltage(chan=2, val=10.0)
        self.set_voltage(chan=3, val=10.0)
        sleep(1)


if __name__ == "__main__":
    psu = DP800("IP", "10.0.142.1")
    while 1:
        psu.set_voltage(chan="2", val="15")
        sleep(0.2)
        psu.set_current(chan="2", val="0.5")
        sleep(0.2)
        psu.set_voltage(chan="3", val="15")
        sleep(0.2)
        psu.set_current(chan="3", val="0.5")
        sleep(0.2)
        psu.toggle_output("2", "ON")
        sleep(0.2)
        psu.toggle_output("3", "ON")
        sleep(0.2)
        chan2 = int(psu.measure_voltage("2"))
        print(chan2)
        chan3 = int(psu.measure_voltage("3"))
        print(chan3)
        continue
        psu.set_voltage("1", "1")
        psu.set_voltage("2", "2")
        psu.set_voltage("3", "3")
        sleep(1)
        psu.set_voltage("1", "2")
        psu.set_voltage("2", "3")
        psu.set_voltage("3", "4")
        sleep(1)
