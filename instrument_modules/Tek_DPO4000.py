"""This module is for implementing remote control of Tektronix
DPO4000 series or MSO4000 series oscilloscopes.

M. Capotosto
3/5/2025
NSLS-II Diagnostics and Instrumentation
"""

# pylint: disable=bare-except
# pylint: disable=broad-except
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name

from time import sleep
from instrument_modules.visa_utils import connect_usb_instrument, \
    connect_ethernet_instrument  # Importing utility module

TIMEOUT = 20000  # VISA Timeout in ms


class DPO4000:
    """Create Tek DPO Class"""
    # *************************************************************************
    # ******Initialize Connection******
    def __init__(self, connection_method, address):
        TIMEOUT = 20000  # VISA Timeout in ms
        if connection_method == "USB":
            self.device, self.address, self.status = \
                connect_usb_instrument(address)
            self.connected_with = 'USB' if self.status == "Connected" else None
        elif connection_method == "IP":
            self.device, self.address, self.status = \
                connect_ethernet_instrument(address)
            self.connected_with = 'Ethernet' \
                if self.status == "Connected" else None
        self.device.timeout = TIMEOUT

    # *************************************************************************
    # ******Status Commands******
    def reset(self):
        self.device.write("*RST")

    def wai(self):
        """define a WAIT function"""
        command = "*WAI"
        self.device.write(command)

    def wait_until_ready(self):
        """Waits until the oscilloscope is ready for the next command."""
        while True:
            try:
                if int(self.device.query("*OPC?")):  # Query if the operation is complete
                    break
            except Exception:
                sleep(0.1)  # Small delay before retrying
    # *************************************************************************
    # ******Horizontal Commands******

    def horizontal_record_length(self, hor_rec_length="10000"):
        """define a HORIZONTAL RECORD LENGTH function"""
        command = f"HOR:RECO {hor_rec_length}"
        self.device.write(command)

    def horizontal_scale(self, hor_scale_length="100e-9"):
        """define a HORIZONTAL SCALE LENGTH function"""
        command = f"HORIZONTAL:SCALE {hor_scale_length}"
        self.device.write(command)

    # *************************************************************************
    # ******VERTICAL Commands******
    def bandwidth(self, chan, bandwidth="FULL"):
        """define a BANDWIDTH function
        VALUES: TWEnty | TWOfifty | FULl | <NR3>
        """
        command = f"CH{chan}:BANDWIDTH {bandwidth}"
        self.device.write(command)

    def coupling(self, chan, coupling="DC"):
        """Define a COUPLING function
        VALUES: AC | DC | GND
        """
        command = f"CH{chan}:COUPLING {coupling}"
        self.device.write(command)

    def deskew(self, chan, delay="0E+00"):
        """Define a DESKEW delay
        Arguments: Time -100ns to +100ns in E- notation
        """
        command = f"CH{chan}:DESKEW {delay}"
        self.device.write(command)

    def invert(self, chan, invert="off"):
        """Invert DISPLAY WAVEFORM"""
        command = f"CH{chan}:INVert {invert}"
        self.device.write(command)

    def label(self, chan, label=""):
        """Set Channel Label"""
        command = f"CH{chan}:LABel {label}"
        self.device.write(command)

    def vertical_position(self, chan, pos=0):
        """Set Vertical Position
        VALUES: -8 to +8 divisions
        """
        command = f"CH{chan}:POSition {pos}"
        self.device.write(command)

    def probe_gain(self, chan, gain="1.0E+00"):
        """Set probe gain/attenuation"""
        command = f"CH{chan}:PROBE:GAIN {gain}"
        self.device.write(command)

    def chan_vertical_scale(self, chan, scale):
        """Set vertical scale
        Values in E-notation
        """
        command = f"CH{chan}:SCALE {scale}"
        self.device.write(command)

    def chan_termination(self, chan, term="MEG"):
        """Sets channel termination
        Values: FIFty | MEG | <NR3>
        """
        command = f"CH{chan}:TERMINATION {term}"
        self.device.write(command)

    def chan_units(self, chan, units="V"):
        """Sets channel units.
        Values: %, /Hz, A, A/A, A/V, A/W, A/dB, A/s, AA, AW, AdB, As, B, Hz,
        IRE, S/s, V, V/A, V/V, V/W, V/dB, V/s, VV, VW, VdB, Volts, Vs, W, W/A,
        W/V, W/W, W/dB, W/s,WA, WV,WW, WdB, Ws, dB, dB/A, dB/V, dB/W, dB/dB,
        dBA, dBV, dBW, dBdB, day, degrees, div, hr, min, ohms, percent, s"""
        command = f"CH{chan}:YUNITS {units}"
        self.device.write(command)

    # *************************************************************************
    # ******Acquire Commands******
    def select_ch(self, chan):
        """Select Channel waveform on/off, select for acq"""
        command = f"SELECT:CH{chan}"
        self.device.write(command)

    def acquire_stopafter(self, stopafter_val="SEQUENCE"):
        """define a ACQUISITION STOP AFTER function"""
        command = f"ACQUIRE:STOPAFTER {stopafter_val}"
        self.device.write(command)

    def acquire_state(self, acq_state="1"):
        """define a ACQUISITION STATE function"""
        command = f"ACQUIRE:STATE {acq_state}"
        self.device.write(command)

    # *************************************************************************
    # ******DATA Commands******
    def data_source(self, chan):
        """define a DATA SOURCE function"""
        command = f"DATA:SOU CH{chan}"
        self.device.write(command)

    def data_width(self, width="1"):
        """define a DATA WIDTH function"""
        command = f"DATA:WIDTH {width}"
        self.device.write(command)

    def data_encoding(self, enc="RPB"):
        """define a DATA ENCODING function"""
        command = f"DATA:ENC {enc}"
        self.device.write(command)

    # *************************************************************************
    # ******WAVEFORM PREAMBLE Commands******
    def wfmpre_ymult(self):
        """Query the vertical scale factor (YMULT) from the
        waveform preamble"""
        command = "WFMPRE:YMULT?"
        try:
            # self.wait_until_ready()
            # print("wait until")
            self.wai()
            ymult = float(self.device.query(command))  # Send query and
            # print("Passed ymult...")
            # convert response to float
            return ymult
        except Exception as e:
            print(f"Error querying YMULT: {e}")
            return None

    def wfmpre_yzero(self):
        """Query the vertical offset (YZERO) from the waveform preamble"""
        command = "WFMPRE:YZERO?"
        try:
            yzero = float(self.device.query(command))  # Send query and
            # convert response to float
            return yzero
        except Exception as e:
            print(f"Error querying YZERO: {e}")
            return None

    def wfmpre_yoff(self):
        """Query the vertical offset (YOFF) from the waveform preamble"""
        command = "WFMPRE:YOFF?"
        try:
            yoff = float(self.device.query(command))  # Send query and convert
            # response to float
            return yoff
        except Exception as e:
            print(f"Error querying YOFF: {e}")
            return None

    def wfmpre_xincr(self):
        """Query the horizontal increment (XINCR) from the waveform preamble"""
        command = "WFMPRE:XINCR?"
        try:
            xincr = float(self.device.query(command))  # Send query and
            # convert response to float
            return xincr
        except Exception as e:
            print(f"Error querying XINCR: {e}")
            return None

# *************************************************************************
# ******DATA COLLECTION FUNCTIONS******

    def config_acq(self, stopafter_val, acq_state):

        """Configure scope acquisition"""
        self.acquire_stopafter(stopafter_val)
        self.acquire_state(acq_state)
        self.wai()

    def acquire_waveform(self, chan, width="1", enc="RPB"):
        """Acquire the waveform"""
        good = 0
        while good == 0:
            try:
                self.data_source(chan)
                self.data_width(width)
                self.data_encoding(enc)
                ymult = float(self.wfmpre_ymult())
                yzero = self.wfmpre_yzero()
                yoff = self.wfmpre_yoff()
                xincr = self.wfmpre_xincr()
                self.device.write("CURVE?")
                data = self.device.read_raw()
                good = 1
            except:  # noqa: E722
                good = 0
        return ymult, yzero, yoff, xincr, data

    def scope_test(self):
        """Scope test"""
        self.vertical_position("1", "1")
        self.vertical_position("2", "2")
        self.vertical_position("3", "3")
        sleep(1)
        self.vertical_position("1", "-1")
        self.vertical_position("2", "-2")
        self.vertical_position("3", "-3")
        self.vertical_position("4", "-5")
        sleep(1)

    def measure_amplitude(self, chan, meastype):
        """Select Channel waveform on/off, select for acq"""
        command = f"MEASUrement:IMMed:SOUrce{chan}"
        self.device.write(command)

        command = f"MEASUrement:IMMed:TYPe{meastype}"
        voltage = self.device.write(command)
        return voltage


if __name__ == "__main__":
    i = 0
    while i < 10:
        scope = DPO4000("IP", "10.0.142.3")
        scope.scope_test()
        scope.reset()
        i += i
