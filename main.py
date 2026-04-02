"""This module is the main module for testing ALSu DCCT Modules.

M. Capotosto
3/5/2025
NSLS-II Diagnostics and Instrumentation"""

import csv
import sys
import os
from time import sleep
from datetime import datetime
from plotter_calculator import plot_waveforms
from functional_tests.fault_test import FLT12_Fault_Test
from functional_tests.current_test import current_test
from instrument_modules.rigol_dp800 import DP800
from instrument_modules.rigol_dg4000 import DG4000
from instrument_modules.Tek_DPO4000 import DPO4000
# from instrument_modules.keithley_2100 import Keithley2100
from instrument_modules.keysight_34461a import Keysight34461A
from report_generator import plot_pdf

SCRIPT_REVISION = 0  # Revision # for report tracking purposes...
# *************************************************************************
# ******Constants******
GEN_TEST_FREQ = "10"  # Set test frequency (Hz)
GEN_TEST_VOLTAGE = "20"  # Set function gen voltage, VPP

# *************************************************************************
# ******Set Insturment IP Addresses******

PSU_IP_ADDRESS = "10.0.143.28"  # Set PSU IP Address here
SIG_GEN_IP_ADDRESS = "10.0.142.2"  # Set signal generator IP Address here
SCOPE_IP_ADDRESS = "10.0.142.3"  # Set oscope IP Address
# DMM_ADDRESS = "USB0::0x05E6::0x2100::8020357::INSTR"
DMM_ADDRESS = "10.0.143.26"

# *************************************************************************


# *************************************************************************
# ******Create Instrument Objects******

psu = DP800(connection_method="IP", address=PSU_IP_ADDRESS)
gen = DG4000(connection_method="IP", address=SIG_GEN_IP_ADDRESS)
scope = DPO4000(connection_method="IP", address=SCOPE_IP_ADDRESS)
# dmm = Keithley2100(connection_method="USB", address=DMM_ADDRESS)
dmm = Keysight34461A(connection_method="IP", address=DMM_ADDRESS)
# *************************************************************************
# *************************************************************************
# ******Initialize Date/Time Names for Test Instance******
# ******Create directory structures for Test Data Storage******


def get_current_datetime():
    """Get formatted date/time"""
    dir_create_time = datetime.now()
    dir_time_formatted = dir_create_time.strftime("%m-%d-%y_%H-%M-%S")
    report_date_formatted = dir_create_time.strftime("%m/%d/%y")
    report_time_formatted_l = dir_create_time.strftime("%I:%M %p")

    return dir_create_time, dir_time_formatted, report_date_formatted, \
        report_time_formatted_l


def create_test_directories(dcct_sn, dir_time_formatted):
    """Create any missing parent directories, make new DCCT directory, raw
    data subdirectories"""
    # Define paths
    report_path = os.path.join("Test_Data", f"DCCT_{dcct_sn}-"
                               f"{dir_time_formatted}",
                               f"DCCT_{dcct_sn}_Report.pdf")
    raw_data_path = f"./Test_Data/DCCT_{dcct_sn}-{dir_time_formatted}/raw_data"

    # Create parent directories for report and raw data paths (not including
    # the file name)
    report_dir = os.path.dirname(report_path)
    os.makedirs(report_dir, exist_ok=True)

    # Create the raw_data directory
    os.makedirs(raw_data_path, exist_ok=True)

    return report_path, raw_data_path
# *************************************************************************

# *************************************************************************
# ******Acquire Test Technician Names...******
# ******Acquire DCCT Information......******


def get_test_tech_info():
    """Acquire static test technician information"""
    while True:
        tester_name = input("Enter your name: ")
        tester_life = input("Enter your Life #: ")

        if input(f"You entered: {tester_name}, {tester_life},"
                 f" is this correct? <Y/N>: ") in ("Y", "y"):
            return tester_name, tester_life


def save_test_tech_info():
    """Save test technician demographics to file"""
    # **********************************************************************************
    # Save test data to file...
    # **********************************************************************************

    file_path_l = os.path.join(raw_data_path, f"{dcct_sn}_Technician_Data.csv")

    data = [
        ["tester_name", "tester_life"],
        [tester_name, tester_life]
    ]

    try:
        # Open the file in write mode (will create the file if it doesn't
        # exist)
        with open(file_path_l, mode='w', newline='', encoding='utf-8') \
                as file_l:
            writer = csv.writer(file_l)

            # Write the header and the data rows
            writer.writerows(data)

        print(f"Tester data saved to: {file_path_l}")

    except OSError as e:
        print(f"Error writing to {file_path_l}: {e}")


def get_dcct_info():
    """Acquire DCCT Serial No./Type Information"""
    while True:
        dcct_sn_raw = input("Enter DCCT S/N: ")
        dcct_sn = dcct_sn_raw[:13]
        if input(f"You entered: {dcct_sn}, is this correct? <Y/N>: ") in \
                ("Y", "y"):
            dir_create_time, dir_time_formatted, report_date_formatted, \
                report_time_formatted = get_current_datetime()
            # Create test data directories
            report_path, raw_data_path = \
                create_test_directories(dcct_sn, dir_time_formatted)

            file_path_l = os.path.join(raw_data_path,
                                       f"{dcct_sn}_raw_label.csv")
            data = [dcct_sn_raw]

            try:
                # Open the file in write mode (will create the file if it
                # doesn't exist)
                with open(file_path_l, mode='w', newline='',
                          encoding='utf-8') as file_l:
                    writer = csv.writer(file_l)

                    # Write the header and the data rows
                    writer.writerows(data)

                print(f"Tester data saved to: {file_path_l}")

            except OSError as e:
                print(f"Error writing to {file_path_l}: {e}")
        return dcct_sn, dir_create_time, dir_time_formatted, \
            report_date_formatted, report_time_formatted, \
            report_path, raw_data_path, dcct_sn_raw


# *************************************************************************
# ******Initialize Instruments******
def psu_init():
    """Initialize PSU"""
    psu.toggle_output("1", "OFF")
    psu.toggle_output("2", "OFF")
    psu.toggle_output("3", "OFF")
    psu.toggle_ovp("2", "OFF")
    psu.toggle_ovp("3", "OFF")
    psu.toggle_ocp("2", "OFF")
    psu.toggle_ocp("3", "OFF")
    psu.set_voltage("1", "0")
    psu.set_voltage("2", "15")
    psu.set_voltage("3", "15")


def gen_init():
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


# *************************************************************************


# *************************************************************************
# ******Run FAULT 1/FAULT2 Testing******
def run_fault_test():
    """Call the fault_test function."""
    while True:
        fault_test = FLT12_Fault_Test(psu, gen, dmm)
        fault_test_results_l = fault_test.run_the_fault_test()
        # **********************************************************************************
        # Save test data to file...
        file_path_l = os.path.join(raw_data_path,
                                   f"{dcct_sn}_fault_test_raw_data.csv")

        try:
            with open(file_path_l, mode='w', encoding='utf-8', newline='') \
                    as file:
                writer = csv.writer(file)

                # Write the header (keys of the dictionary)
                writer.writerow(fault_test_results_l.keys())

                # Write the values (dictionary values in the same order
                # as the keys)
                writer.writerow(fault_test_results_l.values())

            print(f"Fault test results saved to: {file_path_l}")

        except OSError as e:
            print(f"Error writing to {file_path_l}: {e}")

        # ************************************************************************************

        # test_passed is BOOL P/F value
        # flt12_voltage is voltage measured across FLT12 open emitter output
        # n15v_voltage is the N15V rail PSU voltage at the time the
        # FAULT flag asserted
        psu_init()  # Restore PSU voltages.
        print("Cycling DCCT PSU power...\n\n")
        sleep(3)

        if (fault_test_results_l["test_passed"]
                and fault_test_results_l["positive_assertion_test"]
                and fault_test_results_l["negative_assertion_test"]
                and fault_test_results_l["deassertion_test"]):
            print("All FLT12 Status tests passed. Proceeding to DCCT Current "
                  "Testing...\n\n")
            return fault_test_results_l
        else:
            print("One or more FLT12 tests failed.")
            if input("Do you want to repeat FLT12 testing? <Y/N>: ") \
                    not in ("Y", "y"):
                if input("Do you want to restart with a new unit? <Y/N>: ") \
                        in ("Y", "y"):
                    return fault_test_results_l
                else:
                    if input("Proceed to DCCT Current Testing? <Y/N>: ") \
                            in ("Y", "y"):
                        return fault_test_results_l

# **************************************************************************


# *************************************************************************
# ******Run Current Testing******

def run_current_test():
    """Call the run_current_test function."""
    current_channel_data_l, current_decoded_wfdata_l = \
        current_test(gen, psu, scope)

    # **********************************************************************************
    # Save raw data to file...

    # **********************************************************************************
    # Save raw channel data
    file_path_chan_l = os.path.join(raw_data_path,
                                    f"{dcct_sn}_channel_data.csv")
    current_plot_filename_l = os.path.join(raw_data_path,
                                           f"waveform_plots_{dcct_sn}"
                                           f"_{dir_time_formatted}.png")
    try:
        # Open the file in write mode and automatically close when the
        # block is finished
        with open(file_path_chan_l, mode='w', newline='', encoding='utf-8') \
                as file_chan_l:
            writer = csv.writer(file_chan_l)
            header = ["Channel", "Y Multiplier", "Y Zero", "Y Offset",
                      "X Incrementation", "Waveform Data"]
            writer.writerow(header)

            # Write the channel data for each channel inside the open block
            for channel, data in current_channel_data_l.items():
                writer.writerow([channel, data["ymult"], data["yzero"],
                                 data["yoff"], data["xincr"], data["data"]])

        print(f"Raw WF Channel Data saved to: {file_path_chan_l}")

    except OSError as e:
        print(f"Error writing to {file_path_chan_l}: {e}")

    return current_channel_data_l, current_decoded_wfdata_l, \
        current_plot_filename_l
# *************************************************************************
# ******Generate Report Dictionaries/Dataset...******
# *************************************************************************


def generate_report_dataset():
    """Generate data dictionary for the report_generator.py module"""
    dut_info_l = {
        "Title": f"DCCT Test Results for DCCT S/N: {dcct_sn}",
        "Technician": f"{tester_name}",
        "Life": f"{tester_life}",
        "DCCT_sn_raw": f"{dcct_sn_raw}",
        "Date": f"{report_date_formatted}",
        "Time": f"{report_time_formatted}",
        "flt12_test_passed_l": fault_test_results["test_passed"],
        "flt12_positive_assertion_test_passed_l":
            fault_test_results["positive_assertion_test"],
        "flt12_negative_assertion_test_passed_l":
            fault_test_results["negative_assertion_test"],
        "flt12_deassertion_test_passed_l":
            fault_test_results["deassertion_test"],
        "flt12_initial_voltage_l": fault_test_results["initial_voltage"],
        "flt12_positive_signal_voltage_l":
            fault_test_results["positive_assert_pin_voltage"],
        "flt12_negative_signal_voltage_l":
            fault_test_results["negative_assert_pin_voltage"],
        "flt12_positive_psu_voltage_l":
            fault_test_results["positive_assert_ps_voltage"],
        "flt12_negative_psu_voltage_l":
            fault_test_results["negative_assert_ps_voltage"],
        "dcct_sn_raw": dcct_sn_raw,
        "flt12_test_current": fault_test_results["test_current"],
        "current_test_ch1_threshold": ch1_threshold,
        "current_test_ch2_threshold": ch2_threshold,
        "current_test_ch3_threshold": ch3_threshold,
        "current_test_frequency": frequency,
        "current_test_phase_shift": phase_shift,
        "current_test_freq_phase_pass": freq_phase_pass,
        "current_test_vpp1": vpp1,
        "current_test_vpp2": vpp2,
        "current_test_vpp3": vpp3
    }
    return dut_info_l

# *************************************************************************
# ******Carry out the testing...******
# *************************************************************************


tester_name, tester_life = get_test_tech_info()  # Get test technician info


LOOP_FLAG = 1

while LOOP_FLAG == 1:

    dcct_sn, dir_create_time, dir_time_formatted, report_date_formatted, \
            report_time_formatted, report_path, raw_data_path, dcct_sn_raw \
            = get_dcct_info()  # Get DCCT S/N
    # Record the time at the start of the test for reporting, file \
    # naming purposes.
    print("Test data directories created...")
    save_test_tech_info()  # Save technician data to the new test directory...

    input("Confirm all connections are made as per the wiring diagrams.\n\n"
          "Ensure GRAY CT conductors go to GRAY terminal blocks, BLUE "
          "conductors go to BLUE terminal blocks\n\n Press return to"
          " continue...")

    input("\n\n Ensure Kepco PSU is powered on,as well as Rigol PSU, Keithley"
          "DMM, Rigol function generator, and Tek Oscilloscope.\n\n Ensure the"
          " DMM's USB cable is connected to the USB Hub, and the local network"
          "connected to the laptop. \n\n Press Return to continue...")

    input("On the Kepco power supply, ensure the following:\nVOLTAGE CONTROL"
          " Switch: OFF\nCURRENT CONTROL Switch: OFF\nMODE Switch: Doesn't"
          " Care\nPotentiometers: Doesn't Care \n\n"
          "Press Return to continue...")

    input("\n\nEnsure differential probes are powered ON, and set to "
          "x20 Attenuation. Press return to continue...")

    # *************************************************************************
    # ******Initialize Instruments******
    # *************************************************************************
    print("Initializing PSU...")
    psu_init()
    print("Initializing Signal Generator...")
    gen_init()

    # *************************************************************************
    # ******Run DCCT FLT12/FAULT 1/FAULT 2 Test******
    print("Beginning DCCT FLT12 Fault1/Fault2 Test...")
    fault_test_results = run_fault_test()

    # *************************************************************************
    # ******Run DCCT CURRENT Testing******
    print("Beginning DCCT Current test...")
    current_channel_data, current_decoded_wfdata, current_plot_filename = \
        run_current_test()
    current_plot_filename_l = os.path.join(raw_data_path,
                                           f"waveform_plots_{dcct_sn}"
                                           f"_{dir_time_formatted}.png")

    plot_filename, ch1_threshold, ch2_threshold, ch3_threshold, \
        frequency, phase_shift, freq_phase_pass, vpp1, vpp2, vpp3 = \
        plot_waveforms(current_channel_data, current_decoded_wfdata,
                       current_plot_filename_l)

    # Make sure all outputs are off...
    psu.set_voltage(2, 0)
    sleep(0.5)
    psu.set_voltage(3, 0)
    sleep(0.5)
    psu.toggle_output(2, 0)
    sleep(0.5)
    psu.toggle_output(3, 0)
    sleep(0.5)
    gen.output_state(1, "OFF")

    # *************************************************************************
    # ******Generate Report...******
    print("Generating Report...")
    dut_info = generate_report_dataset()
    plot_pdf(dut_info, report_path, current_plot_filename)
    os.startfile(report_path)

    # if input("Do you want to test another unit? <Y/N>: ") not in "Y, y":
    LOOP_FLAG = 0

    # *************************************************************************


print("Exiting...")
sleep(5)
sys.exit(0)
