"""This module tests the DCCT with current flowing through the DCCT

This test requires the Kepco supply be powered, signal gen configured,
and scope configured.

The signal gen drives an AC signal into the Kepco supply, which drives current
into the DCCT.

Diff probes set for 20X attenuation measure the DCCT output on Channel 1 and 2;
Channel 3 monitors the signal generator waveform being driven into the Kepco supply.

This test must ensure that CH1 and CH3 are matched in phase, and CH2 is 180deg out.

The amplitude of the output signal must also be verified to be a valid level.


M. Capotosto
3/8/2025
NSLS-II Diagnostics and Instrumentation"""
from time import sleep
from plotter_calculator import plot_waveforms

# *************************************************************************
# ******Constants******

# Signal Gen:
GEN_TEST_FREQ = "10"  # Set test frequency (Hz)
GEN_TEST_VOLTAGE = "20"  # Set function gen voltage, VPP


# Scope
# Horizontal
TIMEBASE = "50E-03"  # 50ms timebase
HOR_REC_LENGTH = "1000"
# Vertical
VERTSCALE1 = "100E-03"  # Vertical scale CH1 to 100mV/div
VERTSCALE2 = "100E-03"  # Vertical scale CH2 to 100mV/div
VERTSCALE3 = "10E+00"  # Vertical scale CH3 to 10V/div
VERTSCALE4 = "2E+00"  # Vertical scale CH3 to 10V/div

# Input Config
CH1_GAIN = "0.20E+00"  # CH1 Attenuation: 20x
CH2_GAIN = "0.20E+00"  # CH2 Attenuation: 20x
CH3_GAIN = "0.00E+00"  # CH3 Attenuation: 1x
CH4_GAIN = "0.00E+00"  # CH4 Attenuation: 1x

CH1_TERMINATION = "MEG"  # 1M Input Impedance
CH2_TERMINATION = "MEG"  # 1M Input Impedance
CH3_TERMINATION = "MEG"  # 1M Input Impedance
CH4_TERMINATION = "MEG"  # 1M Input Impedance
# *************************************************************************


def init_psu_ct(psu):
    """Configure initial conditions for the PSU"""
    psu.set_voltage("1", "0")
    psu.set_voltage("2", "15")
    psu.set_voltage("3", "15")
    psu.toggle_output("2", "ON")
    psu.toggle_output("3", "ON")


def init_scope_ct(scope):
    """Configure initial conditions for the scope..."""
    scope.horizontal_record_length(HOR_REC_LENGTH)
    scope.horizontal_scale(TIMEBASE)
    scope.wai()  # Prevents execution of commands until all pending ops finish

    scope.probe_gain("1", CH1_GAIN)
    scope.probe_gain("2", CH2_GAIN)
    scope.probe_gain("3", CH3_GAIN)
    scope.probe_gain("4", CH4_GAIN)

    scope.chan_termination("1", CH1_TERMINATION)
    scope.chan_termination("2", CH2_TERMINATION)
    scope.chan_termination("3", CH3_TERMINATION)
    scope.chan_termination("4", CH4_TERMINATION)

    scope.chan_vertical_scale("1", VERTSCALE1)
    scope.chan_vertical_scale("2", VERTSCALE2)
    scope.chan_vertical_scale("3", VERTSCALE3)
    scope.chan_vertical_scale("4", VERTSCALE4)
    ##################################################################################
    ##################################################################################
    ##################################################################################
    ##################################################################################
    ##################################################################################
    # ADD TRIGGER CONFIG............................................................
    # ........................................................................
    # .........................................................
    for i in range(1, 4):  # Iterate through settings for Channel 1 through 4 identically...
        scope.bandwidth(str(i), "FULL")
        scope.coupling(str(i), "DC")
        scope.deskew(str(i))
        scope.invert(str(i))
        scope.vertical_position(str(i))
    scope.vertical_position("4", "-5")


def gen_init_ct(gen):
    """Iniitalize signal generator"""
    gen.output_state("1", "OFF")
    sleep(0.5)
    gen.output_state("2", "OFF")
    sleep(0.5)
    gen.output_impedance("1", "INFINITY")
    sleep(0.5)
    gen.output_polarity("1", "NORM")
    sleep(0.5)
    gen.source_fixed_freq("1", GEN_TEST_FREQ)
    sleep(0.5)
    gen.source_function_shape_wave("1", "SIN")
    sleep(0.5)
    gen.source_voltage_level("1", GEN_TEST_VOLTAGE)
    sleep(0.5)
    gen.source_voltage_unit("1", "VPP")
    sleep(0.5)


def acquire_wfdata(scope):
    # PG555
    """Acquire single shot waveform"""
    scope.acquire_state("OFF")
    scope.config_acq("SEQUENCE", "OFF")  # Set for single shot
    scope.acquire_state("ON")  # Wait for a trigger and take a shot
    scope.wai()  # Wait for the acquisition to complete...
    scope.acquire_state("OFF")
    # scope.measurement_gating("SCREEN")

    channel_data = {}
    for i in range(1, 4):
        j = str(i)

        ymult, yzero, yoff, xincr, data = scope.acquire_waveform((j), "1", "RPB")

        channel_data[i] = {
            "ymult": ymult,
            "yzero": yzero,
            "yoff": yoff,
            "xincr": xincr,
            "data": data
        }
    return channel_data


def decode_wfdata(channel_data):
    """Decode waveform data"""
    decoded_wfdata = {}
    for i in range(1, 4):
        data = channel_data[i]["data"]
        headerlen = 2 + int(data[1])  # Access the second byte in the raw wfdata
        header = data[:headerlen]
        adc_wave = data[headerlen:-1]

        decoded_wfdata[i] = {
            "headerlen": headerlen,
            "header": header,
            "adc_wave": adc_wave
        }
    return decoded_wfdata


def current_test(gen, psu, scope):
    """Current Test function"""
    print("Initializing instruments...\n")
    gen.output_state("1", "OFF")
    init_psu_ct(psu)
    sleep(0.5)
    ch2v = psu.measure_voltage("2")
    sleep(1)
    ch3v = abs(psu.measure_voltage("3"))
    sleep(1)
    while not ((ch2v > 14.5) and (abs(ch3v) > 14.5)):
        psu.set_voltage("2", "15")
        sleep(1)
        psu.set_voltage("3", "15")
        sleep(1)
        ch2v = psu.measure_voltage("2")
        sleep(1)
        ch3v = psu.measure_voltage("3")
    if ((ch2v > 14.5) and (abs(ch3v) > 14.5)):
        print(f"CH2V: {ch2v}, CH3V: {ch3v}")
        sleep(0.5)
        gen_init_ct(gen)
        gen.output_state("1", "ON")
    else:
        while not ((ch2v > 14.5) and (abs(ch3v) > 14.5)):
            psu.set_voltage("2", "15")
            sleep(1)
            psu.set_voltage("3", "15")
            sleep(1)
            ch2v = psu.measure_voltage("2")
            sleep(1)
            ch3v = psu.measure_voltage("3")
    sleep(1)
    init_scope_ct(scope)
    sleep(1)
    channel_data = acquire_wfdata(scope)
    sleep(1)
    decoded_wfdata = decode_wfdata(channel_data)
    sleep(1)
    return channel_data, decoded_wfdata


if __name__ == "__main__":
    from datetime import datetime
    import os
    from instrument_modules.Tek_DPO4000 import DPO4000
    from instrument_modules.rigol_dg4000 import DG4000
    from instrument_modules.rigol_dp800 import DP800
    dcct_sn = "abcd"
    SIG_GEN_IP_ADDRESS = "10.0.142.2"  # Set signal generator IP Address here
    SCOPE_IP_ADDRESS = "10.0.142.3"  # Set oscope IP Address
    sig_gen_standalone = DG4000(connection_method="IP", address=SIG_GEN_IP_ADDRESS)
    scope_standalone = DPO4000(connection_method="IP", address=SCOPE_IP_ADDRESS)
    psu_standalone = DP800(connection_method="IP", address="10.0.142.1")

    def create_test_directories(dcct_sn, dir_time_formatted):  # pylint: disable=redefined-outer-name
        """Create any missing parent directories, make new DCCT directory, raw data subdirectories"""
        report_path = f"./Test_Data/DCCT_{dcct_sn}-{dir_time_formatted}/DCCT_{dcct_sn}_Report.pdf"  # noqa: E501 # pylint: disable=redefined-outer-name
        raw_data_path = f"./Test_Data/DCCT_{dcct_sn}-{dir_time_formatted}/raw_data"  \
            # pylint: disable=redefined-outer-name

        os.makedirs(report_path, exist_ok=True)
        os.makedirs(raw_data_path, exist_ok=True)

        return report_path, raw_data_path

    def get_current_datetime():
        """Get formatted date/time"""
        dir_create_time = datetime.now()  # pylint: disable=redefined-outer-name
        dir_time_formatted = dir_create_time.strftime("%m-%d-%y_%H-%M-%S")  # pylint: disable=redefined-outer-name
        report_date_formatted = dir_create_time.strftime("%m/%d/%y")  # pylint: disable=redefined-outer-name
        report_time_formatted_l = dir_create_time.strftime("%I:%M %p")

        return dir_create_time, dir_time_formatted, report_date_formatted, \
            report_time_formatted_l

    dir_create_time, dir_time_formatted, report_date_formatted, \
        report_time_formatted_l = get_current_datetime()

    report_path, raw_data_path = create_test_directories(dcct_sn,
                                                         dir_time_formatted)
    current_channel_data, current_decoded_wfdata = current_test(sig_gen_standalone, psu_standalone, scope_standalone)
    current_plot_filename_l = os.path.join(raw_data_path, f"waveform_plots_{dcct_sn}"
                                                          f"_{dir_time_formatted}.png")
    plot_waveforms(current_channel_data, current_decoded_wfdata, current_plot_filename_l)
