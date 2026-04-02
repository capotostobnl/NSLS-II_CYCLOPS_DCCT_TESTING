# pylint: disable=broad-except
"""This module is for implementing remote control of Keithley 2100
series multimeters.

M. Capotosto
3/5/2025
NSLS-II Diagnostics and Instrumentation
"""

from time import sleep
from instrument_modules.visa_utils import connect_usb_instrument

DELAY = 0.01  # 10ms delay


class Keithley2100:
    """Create Signal Generator Class"""
    # *************************************************************************
    # ******Initialize Connection******
    # Keithely 2100s are USB Only. Ethernet connection method omitted.
    def __init__(self, connection_method, address):
        if connection_method == "USB":
            self.device, self.address, self.status = \
                connect_usb_instrument(address)
            self.connected_with = 'USB' if self.status == "Connected" else None

    # *************************************************************************
    # ******Factory Reset******
    def factory_reset(self):
        """define a FACTORY RESET function"""
        command = "*RST"
        self.device.write(command)
        sleep(5)  # 5 second delay to wait for reset to finish...

    # *************************************************************************
    # MEASure COMMAND SET

    def meas_dcv(self, meas_range="100", resolution="DEF"):
        """Measure DC Volts"""
        command = f"MEASURE:VOLTAGE:DC? {meas_range},{resolution}"
        try:
            dcv = float(self.device.query(command))
            return dcv

        except Exception as e:
            print(f"Error querying MEASURE:VOLTAGE:DC {e}")
            return None

    def meas_res(self, meas_range="100", resolution="DEF"):
        """Measure resistance"""
        command = f"MEASURE:RESISTANCE? {meas_range},{resolution}"
        try:
            res = float(self.device.query(command))
            return res

        except Exception as e:
            print(f"Error querying MEASURE:RESISTANCE? {e}")
            return None

    def dmm_test(self):
        """DMM Test"""
        vout = self.meas_dcv(100)
        sleep(1)
        print(f"DC Volts Measured: {vout}")
        res = self.meas_res()
        sleep(1)
        print(f"Measured resistance out: {res}")


if __name__ == "__main__":  # Standalone execution perform this demo test...
    DMMSN = 8020357
    DMM_ADDRESS = 'USB0::0x05E6::0x2100::'+str(DMMSN)+'::INSTR'
    print("Standalone Execution...Begin Voltage Measurement Test")
    dmm_standalone = Keithley2100(connection_method="USB", address=DMM_ADDRESS)
    dmm_standalone.factory_reset()
    DCV = dmm_standalone.meas_dcv()
    print(f"{int(DCV)} Volts DC")
