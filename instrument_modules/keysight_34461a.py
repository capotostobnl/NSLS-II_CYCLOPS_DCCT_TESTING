# pylint: disable=broad-except
"""This module is for implementing remote control of the Keysight 34461A
Digital Multimeter (DMM).

M. Capotosto
10/29/2025
NSLS-II Diagnostics and Instrumentation
"""

from time import sleep
# Import the existing connection utilities directly
from .visa_utils import connect_usb_instrument, connect_ethernet_instrument

DELAY = 0.01  # 10ms delay


class Keysight34461A:
    """
    Driver class for the Keysight 34461A Digital Multimeter.

    Note: Core measurement commands match the Keithley DMM command set for
    easy interchangeability.
    """
    # *************************************************************************
    # ******Initialize Connection******
    def __init__(self, connection_method, address):
        """
        Initializes the Keysight 34461A DMM connection.

        Parameters:
            connection_method (str): 'USB' or 'IP'.
            address (str): The VISA resource string (USB) or IP address (IP).
        """
        if connection_method == "USB":
            self.device, self.address, self.status = \
                connect_usb_instrument(address)
            self.connected_with = 'USB' if self.status == "Connected" else None
        elif connection_method == "IP":
            # Keysight DMMs often use the standard TCPIP::IP::INSTR setup
            self.device, self.address, self.status = \
                connect_ethernet_instrument(address)
            self.connected_with = 'Ethernet' \
                if self.status == "Connected" else None
        else:
            self.device, self.address, self.status = \
                None, None, "Invalid Method"
            self.connected_with = None

        if self.status == "Connected":
            print(f"Successfully connected to Keysight 34461A via "
                  f"{self.connected_with} at {self.address}")
            # Set a standard timeout for safety (though connect functions
            # already set it)
            if self.device:
                self.device.timeout = 5000

    # *************************************************************************
    # ******Factory Reset******
    def factory_reset(self):
        """Define a FACTORY RESET function (*RST)"""
        command = "*RST"
        self.device.write(command)
        sleep(5)  # 5 second delay to wait for reset to finish...

    # *************************************************************************
    # MEASure COMMAND SET - MIMICKING KEITHLEY DMM COMMANDS

    def meas_dcv(self, meas_range="AUTO", resolution="DEF"):
        """
        Measure DC Volts. (Mimics Keithley2100 meas_dcv)

        Parameters:
            meas_range (str/float): The voltage range (e.g., '10', 'AUTO').
            resolution (str/float): The measurement resolution (e.g., '1e-6',
                                    'DEF').
        Returns:
            float: The measured DC voltage, or None if an error occurs.
        """
        # Keysight SCPI: MEASure:VOLTage:DC? [range][,resolution]
        command = f"MEASURE:VOLTAGE:DC? {meas_range},{resolution}"
        try:
            dcv = float(self.device.query(command))
            return dcv

        except Exception as e:
            print(f"Error querying MEASURE:VOLTAGE:DC: {e}")
            return None

    def meas_res(self, meas_range="AUTO", resolution="DEF"):
        """
        Measure resistance. (Mimics Keithley2100 meas_res)

        Parameters:
            meas_range (str/float): The resistance range (e.g., '1e3', 'AUTO').
            resolution (str/float): The measurement resolution (e.g., '1e-3',
                                    'DEF').
        Returns:
            float: The measured resistance, or None if an error occurs.
        """
        # Keysight SCPI: MEASure:RESistance? [range][,resolution]
        command = f"MEASURE:RESISTANCE? {meas_range},{resolution}"
        try:
            res = float(self.device.query(command))
            return res

        except Exception as e:
            print(f"Error querying MEASURE:RESISTANCE: {e}")
            return None

    def dmm_test(self):
        """
        A simple demonstration test for the DMM functionality.
        """
        if self.status != "Connected":
            print("Cannot run test, device not connected.")
            return

        print("--- Keysight 34461A Demo Test ---")
        self.factory_reset()

        # Test DC Voltage measurement
        vout = self.meas_dcv(meas_range="10")
        sleep(1)
        if vout is not None:
            print(f"DC Volts Measured (10V range, Auto Resolution): {vout} V")

        # Test Resistance measurement
        res = self.meas_res(meas_range="AUTO")
        sleep(1)
        if res is not None:
            print(f"Measured Resistance (Auto range, Auto Resolution): "
                  f"{res} Ohms")

        print("--- Demo Test Complete ---")


if __name__ == "__main__":
    # Example usage for standalone execution (replace with your actual address)
    # Use your Keysight DMM's actual address.

    # Example IP address (common for Keysight)
    DMM_ADDRESS_IP = '192.168.1.100'

    # Example USB address (check Keysight IO Libraries Suite)
    # DMM_ADDRESS_USB = 'USB0::0x0957::0x0701::MY53001234::INSTR'

    print("Standalone Execution... Attempting connection via IP")

    dmm = Keysight34461A(connection_method="IP", address=DMM_ADDRESS_IP)

    if dmm.status == "Connected":
        dmm.dmm_test()
    else:
        print(f"Could not connect to DMM at {DMM_ADDRESS_IP}. "
              f"Check connection and VISA address.")
