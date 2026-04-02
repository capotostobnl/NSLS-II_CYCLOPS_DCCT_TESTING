"""This module is for implementing remote control of Rigol DG4000
series signal generators.

M. Capotosto
3/4/2025
NSLS-II Diagnostics and Instrumentation
"""
from time import sleep
from instrument_modules.visa_utils import connect_usb_instrument, \
    connect_ethernet_instrument  # Importing utility module

DELAY = 0.01  # 10ms delay


class DG4000:
    """Create Signal Generator Class"""
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

    def idn(self):
        """Query the IDN"""
        idn_response = self.device.write("*IDN?")
        return idn_response

    def get_idn(self):
        """Measure resistance"""
        command = "*IDN?"
        idn = self.device.query(command)
        return idn

    # *************************************************************************
    # ******Factory Reset******
    def factory_reset(self):
        """define a FACTORY RESET function"""
        command = "*RST"
        self.device.write(command)
        sleep(5)  # 5 second delay to wait for reset to finish...

    # *************************************************************************
    # Output Configuration

    def output_impedance(self, chan, impedance="INF"):
        """define an OUTPUT IMPEDANCE function
        Range: 1 ohm to 10k ohm
        Options: Integer value within range
        INFinity
        MINimum
        MAXimum
        """
        command = f":OUTP{chan}:IMP {impedance}"
        self.device.write(command)
        sleep(DELAY)

    def noise_state(self, chan, noise_state_val):
        """Define a NOISE STATE function
        BOOL ON or OFF
        """
        command = f":OUTP{chan}:NOIS:STAT {noise_state_val}"
        self.device.write(command)
        sleep(DELAY)

    def noise_scale(self, chan, noise_scale_val):
        """Define a NOISE SCALE function
        Range 0% to 50%
        """
        command = f":OUTP{chan}:NOIS:SCAL {noise_scale_val}"
        self.device.write(command)
        sleep(DELAY)

    def output_polarity(self, chan, output_polarity_val):
        """Define an OUTPUT POLARITY function
        Values: NORMal|INVerted
        """
        command = f":OUTP{chan}:POL {output_polarity_val}"
        self.device.write(command)
        sleep(DELAY)

    def output_state(self, chan, output_state_val):
        """Define an OUTPUT STATE function
        Values: ON|OFF
        """
        command = f":OUTP{chan}:STAT {output_state_val}"
        self.device.write(command)
        sleep(DELAY)

    def sync_polarity(self, chan, sync_polarity_val):
        """Define a SYNC POLARITY function
        Values: POSitive|NEGative
        """
        command = f":OUTP{chan}:SYNC:POL {sync_polarity_val}"
        self.device.write(command)
        sleep(DELAY)

    def sync_state(self, chan, sync_state_val):
        """Define a SYNC STATE function
        Values: ON|OFF
        """
        command = f":OUTP{chan}:SYNC:STAT {sync_state_val}"
        self.device.write(command)
        sleep(DELAY)

    # *************************************************************************
    # ******Source Frequency Configuration******
        # Values:
        # Sine: 1 μHz to 160 MHz
        # Square: 1 μHz to 50 MHz
        # Ramp: 1 μHz to 4 MHz
        # Arb: 1 μHz to 40 MHz (except DC in the built-in waveforms)

    def source_center_freq(self, chan, source_center_freq_val):
        """Define a SOURCE CENTER FREQ function"""
        command = f":SOUR{chan}:FREQ:CENT {source_center_freq_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_fixed_freq(self, chan, source_fixed_freq_val):
        """Define a SOURCE FIXED FREQ function"""
        command = f":SOUR{chan}:FREQ:FIX {source_fixed_freq_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_span_freq(self, chan, source_span_freq_val):
        """Define a SOURCE SPAN FREQ function"""
        command = f":SOUR{chan}:FREQ:SPAN {source_span_freq_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_start_freq(self, chan, source_start_freq_val):
        """Define a SOURCE START FREQ function"""
        command = f":SOUR{chan}:FREQ:STAR {source_start_freq_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_stop_freq(self, chan, source_stop_freq_val):
        """Define a SOURCE STOP FREQ function"""
        command = f":SOUR{chan}:FREQ:STOP {source_stop_freq_val}"
        self.device.write(command)
        sleep(DELAY)

    # *************************************************************************
    # ******Source Function Configuration******
    def source_function_arb_step(self, chan, source_function_arb_step_val):
        """Define a SOURCE FUNCTION ARB STEP function"""
        command = f":SOUR{chan}:FUNC:ARB:STEP {source_function_arb_step_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_function_ramp_symmetry(self, chan,
                                      source_function_ramp_symmetry_val):
        """Define a SOURCE FUNCTION RAMP SYMMETRY function"""
        command = f":SOUR{chan}:FUNC:RAMP:SYMM \
            {source_function_ramp_symmetry_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_function_shape_wave(self, chan, source_function_shape_wave_val):
        """Define a SOURCE FUNCTION SHAPE WAVE function

        Values: SINusoid|SQUare|RAMP|PULSe|NOISe|USER|HARMonic|CUSTom|DC|
        ABSSINE|ABSSINEHALF|AMPALT|ATTALT|GAUSSPULSE|NEGRAMP|NPULSE|PPULSE|SINETRA|
        SINEVER|STAIRDN|STAIRUD|STAIRUP|TRAPEZIA|BANDLIMITED|BUTTERWORTH|CHEBYSHEV1|
        CHEBYSHEV2|COMBIN|CPULSE|CWPULSE|DAMPEDOSC|DUALTONE|GAMMA|GATEVIBR|LFMPULSE|
        MCNOSIE|NIMHDISCHARGE|PAHCUR|QUAKE|RADAR|RIPPLE|ROUNDHALF|ROUNDPM|STEPRESP|
        SWINGOSC|TV|VOICE|THREEAM|THREEFM|THREEPM|THREEPWM|THREEPFM|CARDIAC|EOG|EEG|
        EMG|PULSILOGRAM|RESSPEED|LFPULSE|TENS1|TENS2|TENS3|IGNITION|ISO167502SP|
        ISO167502VR|ISO76372TP1|ISO76372TP2A|ISO76372TP2B|ISO76372TP3A|ISO76372TP3B|
        ISO76372TP4|ISO76372TP5A|ISO76372TP5B|SCR|SURGE|AIRY|BESSELJ|BESSELY|CAUCHY|
        CUBIC|DIRICHLET|ERF|ERFC|ERFCINV|ERFINV|EXPFALL|EXPRISE|GAUSS|HAVERSINE|LAGUERRE|
        LAPLACE|LEGEND|LOG|LOGNORMAL|LORENTZ|MAXWELL|RAYLEIGH|VERSIERA|WEIBULL|X2DATA|COSH|
        COSINT|COT|COTHCON|COTHPRO|CSCCON|CSCPRO|CSCHCON|CSCHPRO|RECIPCON|RECIPPRO|SECCON|
        SECPRO|SECH|SINC|SINH|SININT|SQRT|TAN|TANH|ACOS|ACOSH|ACOTCON|ACOTPRO|ACOTHCON|
        ACOTHPRO|ACSCCON|ACSCPRO|ACSCHCON|ACSCHPRO|ASECCON|ASECPRO|ASECH|ASIN|ASINH|ATAN|
        ATANH|BARLETT|BARTHANN|BLACKMAN|BLACKMANH|BOHMANWIN|BOXCAR|CHEBWIN|FLATTOPWIN|HAMMING|
        HANNING|KAISER|NUTTALLWIN|ARZENWIN|TAYLORWIN|TRIANG|TUKEYWIN

        """

        command = f":SOUR{chan}:FUNC:SHAP {source_function_shape_wave_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_function_square_dcycle(self, chan,
                                      source_function_square_dcycle_val):
        """Define a SOURCE FUNCTION SQUARE DUTY CYCLE function
        Value: 0 to 100% real numbers only
        """
        command = f":SOUR{chan}:FUNC:SQU:DCYC \
            {source_function_square_dcycle_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_function_pulse_dcycle(self, chan,
                                     source_function_pulse_dcycle_val):
        """Define a SOURCE FUNCTION PULSE DUTY CYCLE function
        Value: 0 to 100% real numbers only
        """
        command = f":SOUR{chan}:PULSe:DCYC"
        f"{source_function_pulse_dcycle_val}"
        self.device.write(command)
        sleep(DELAY)

    # *************************************************************************
    # ******Source Voltage Configuration******

    def source_voltage_level(self, chan, source_voltage_level_val):
        """Define a SOURCE VOLTAGE LEVEL function
        Default VPP
        """
        command = f":SOUR{chan}:VOLT:LEV:IMM:AMPL {source_voltage_level_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_voltage_high(self, chan, source_voltage_high_val):
        """Define a SOURCE VOLTAGE HIGH LEVEL function
        Unit: Volts
        Range up to 10V HighZ or 5V into 50R
        """
        command = f":SOUR{chan}:VOLT:LEV:IMM:HIGH {source_voltage_high_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_voltage_low(self, chan, source_voltage_low_val):
        """Define a SOURCE VOLTAGE LOW LEVEL function
        Unit: Volts
        Range up to -10V HighZ or -5V into 50R
        """
        command = f":SOUR{chan}:VOLT:LEV:IMM:LOW {source_voltage_low_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_voltage_offset(self, chan, source_voltage_offset_val):
        """Define a SOURCE VOLTAGE OFFSET LEVEL function
        Unit: Volts
        """
        command = f"SOURce{chan}:VOLT:OFFS: {source_voltage_offset_val}"
        self.device.write(command)
        sleep(DELAY)

    def source_voltage_unit(self, chan, source_voltage_unit_val):
        """Define a SOURCE VOLTAGE UNIT function
        Values: VPP|VRMS|DBM
        """
        command = f":SOURCE{chan}:VOLT:UNIT {source_voltage_unit_val}"
        self.device.write(command)
        sleep(DELAY)

    def gen_test(self):
        """Function Gen test"""
        self.source_voltage_unit("1", "VPP")
        self.source_voltage_level("1", "1")
        sleep(1)
        self.source_voltage_level("1", "10")
        sleep(1)

    def apply_pulse(self, chan, freq, amp,   offset, delay_l):
        command = f":SOURce{chan}:APPLy:PULSe {freq}, {amp}, {offset}, {delay_l}"
        self.device.write(command)


if __name__ == "__main__":
    sg = DG4000(connection_method="IP", address="10.0.142.2")
    while True:
        sg.source_voltage_unit("1", "VPP")
        # sg.source_voltage_high("1", "10")
        sg.source_voltage_level("1", "20")
        sleep(1)
        # sg.source_voltage_unit("1", "VRMS")
        sg.source_voltage_level("1", "0")
        sleep(1)
        GEN_TEST_VOLTAGE = 1
        sg.apply_pulse("1", "0.001", "0.005", GEN_TEST_VOLTAGE, "0")
        sleep(1)
        GEN_TEST_VOLTAGE = -1
        sg.apply_pulse("1", "0.001", "0.005", GEN_TEST_VOLTAGE, "0")
