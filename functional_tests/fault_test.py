# flake8: noqa E501
"""This module tests the FLT12 fault output status.

M. Capotosto
3/13/2025
NSLS-II Diagnostics and Instrumentation


This FLT12 Fault output is an OPEN EMITTER output.

When a fault is ASSERTED, the FLT12 status voltage is: LOW, via floating the emitter (Testbed has 10k R to ground).
When a fault is CLEARED, the FLT12 Status voltage is: HIGH via optoisolator to +15V inside chassis.

A fault is asserted by decrementing the -15V supply in 250mV steps, starting at 10V
until fault is in ASSERTED state. The voltage is measured.

The fault is an "ACTIVE LOW": FLT12 Pin is pulled up to +15V
under normal operating conditions.
"""
from time import sleep
import numpy as np



class FLT12_Fault_Test:
    N15V_THRES_HIGH = 15  # -15V threshold upper limit for pass/fail testing
    N15V_THRES_LOW = 1  # -15V Threshold lower limit for pass/fail testing. **BELOW 1V, FAULT BIT WON'T TOGGLE**
    FLT12_ASSERT = 1  # Threshold voltage for FLT12 Fault Assertion
    FLT12_DEASSERT = 13.5  # Threshold voltage for FLT12 Fault De-Assertion
    GEN_TEST_FREQ = "0.001"  # Set test frequency (Hz)
    GEN_TEST_VOLTAGE = 1  # Set function gen voltage, VPP
    GEN_TEST_VOLTAGE_NEG = -1

    def __init__(self, psu, gen, dmm):
        self.psu = psu
        self.gen = gen
        self.dmm = dmm

    def init_psu(self):
        """Initialize PSU for the start of the test"""
        self.psu.set_voltage(chan="2", val="15")
        sleep(0.5)
        self.psu.set_current(chan="2", val="0.1")
        sleep(0.5)
        self.psu.set_voltage(chan="3", val="15")
        sleep(0.5)
        self.psu.set_current(chan="3", val="0.1")
        sleep(0.5)
        self.psu.toggle_output("2", "ON")
        sleep(0.5)
        self.psu.toggle_output("3", "ON")
        sleep(0.5)
        chan2 = self.psu.measure_voltage("2")
        sleep(0.5)
        chan3 = self.psu.measure_voltage("3")
        sleep(0.5)
        return chan2, chan3

    def gen_init(self):
        """Initialize signal generator"""
        self.gen.source_voltage_level("1", "1")
        sleep(0.5)
        self.gen.output_state("1", "OFF")
        sleep(0.5)
        self.gen.output_state("2", "OFF")
        sleep(0.5)
        self.gen.output_impedance("1", "INF")
        sleep(0.5)
        self.gen.output_polarity("1", "NORM")
        sleep(0.5)
        self.gen.source_fixed_freq("1", self.GEN_TEST_FREQ)
        sleep(0.5)
        self.gen.source_function_shape_wave("1", "PULSE")
        sleep(0.5)
        self.gen.source_voltage_offset("1", self.GEN_TEST_VOLTAGE)
        sleep(0.5)
        self.gen.source_voltage_level("1", "0.002")
        sleep(0.5)
        self.gen.source_function_pulse_dcycle("1", "MAX")
        sleep(0.5)
        self.gen.source_voltage_unit("1", "VPP")
        sleep(0.5)
        self.gen.apply_pulse("1", self.GEN_TEST_FREQ, "0.005", self.GEN_TEST_VOLTAGE, "0")
        sleep(3)

    def init_dmm(self):
        self.dmm.factory_reset()

    def run_the_fault_test(self):
        """Fault Test Procedure"""
        ##############################################################################################
        # ******Initialize Instruments...******
        ##############################################################################################
        print("Beginning FLT12 Fault Test...\n")
        print("Initializing Instruments...\n")
        chan2, chan3 = self.init_psu()
        while chan2 < 14.75 and abs(chan3) < 14.75:
            print("Error configuring self.psu...retrying...")
            chan2, chan3 = self.init_psu()
        self.gen_init()
        self.gen.output_state("1", "ON")
        sleep(1)
        self.init_dmm()
        sleep(1)
        ###############################################################################################

        ##############################################################################################
        # ******Find FLT12 Initial Voltage...******
        ##############################################################################################
        # print(self.flt12_initial_voltage)
        self.flt12_initial_voltage = round(self.dmm.meas_dcv(), 4)
        print(self.flt12_initial_voltage)
        sleep(0.5)
        if self.flt12_initial_voltage >= self.FLT12_DEASSERT:
            flt12_deassertion_test_passed = True
            print(f"De-Assert/Initial Voltage Test Passed!  {round(self.flt12_initial_voltage, 3)} Volts..."
                  "Continuing to remaining tests...\n")
            self.flt12_flag = False  # FLT12 Status Flag Initializaiton
        else:
            flt12_deassertion_test_passed = False
            print("De-Assert Voltage too low! Test failed! Continuing to remaining tests...\n")
            self.flt12_flag = True  # FLT12 Status Flag Initializaiton
        ###############################################################################################

        ##############################################################################################
        # ******Test Positive FLT12 Fault******
        ##############################################################################################
        flt12_positive_assert_pin_voltage = round(self.dmm.meas_dcv(), 4)  # Create a valid initial \
        # value for the while loop...
        self.gen.apply_pulse("1", self.GEN_TEST_FREQ, "0.005", self.GEN_TEST_VOLTAGE_NEG, "0")
        self.psu.set_voltage("3", "10")  # Drop PSU N15V to 10V to expedite testing...
        sleep(1)
        N15V_setpoint = self.psu.measure_voltage("3")
        psu_rb = N15V_setpoint  # Initialize psu_rb before the loop print statements...
        sleep(1)

        while ((flt12_positive_assert_pin_voltage >= self.FLT12_ASSERT) and (abs(N15V_setpoint) >=
                                                                             self.N15V_THRES_LOW)):
            # Repeat until fault is asserted...
            flt12_positive_assert_pin_voltage = round(self.dmm.meas_dcv(), 4)
            sleep(1)
            print(f"PSU N15V Rail Voltage: {psu_rb} \n"
                  f"FLT12 Fault Status Voltage:{np.round(flt12_positive_assert_pin_voltage, 3)} \n"
                  f"FLT12 Fault Status Flag: {self.flt12_flag}")
            # input(f"pre-sp increase... 249....{N15V_setpoint}")
            N15V_setpoint += 0.250
            # input(f"Post-sp increase...{N15V_setpoint}")
            psu_rb = self.psu.measure_voltage("3")
            sleep(1)
            # input(f"while ({N15V_setpoint - 0.02}) <= {psu_rb} <= ({N15V_setpoint + 0.02})")
            while not ((N15V_setpoint - 0.02) <= psu_rb <= (N15V_setpoint + 0.02)):  \
                    # Command PSU to drop 250mV until readback shows it does...
                print("Adjusting PSU voltage...retrying...")
                psu_sp = str(N15V_setpoint)
                print(f"DBUG PSU SP: {psu_sp}")
                self.psu.set_voltage("3", psu_sp)
                sleep(1)
                psu_rb = self.psu.measure_voltage("3")
                sleep(1)
                # input(f"PSU RB 260: {psu_rb}")
            print("PSU Voltage adjusted, re-acquiring data...")
        # loop...FLT12 is now ASSERTED...
        # input(f"DBUG: 267: fell out of while cond. (({flt12_assert_pin_voltage} >= {FLT12_DEASSERT}) and \
        # ({abs(N15V_setpoint)} >= {N15V_THRES_HIGH})):")
        flt12_flag = True
        flt12_positive_assert_ps_voltage = psu_rb  # Store the final value that caused assert

        print(f"PSU N15V Rail Voltage: {psu_rb} \n"
              f"FLT12 Fault Status Voltage: {flt12_positive_assert_pin_voltage} \n"
              f"FLT12 Fault Status Flag: {flt12_flag}\n\n\n")
        sleep(0.5)
        if ((flt12_flag is True) and (abs(psu_rb) >= self.N15V_THRES_LOW) and (abs(psu_rb) <= self.N15V_THRES_HIGH)):
            print("FLT12 Positive Assertion Test passed!\n")
            flt12_positive_assertion_test_passed = True
        else:
            print("FLT12 Positive Assertion Test failed: N15V is outside threshold!\n")
            flt12_positive_assertion_test_passed = False
        self.psu.toggle_output("2", "OFF")
        sleep(0.5)
        self.psu.toggle_output("3", "OFF")
        sleep(0.5)
        self.psu.set_voltage(chan="2", val="15")
        sleep(0.5)
        self.psu.set_voltage(chan="3", val="15")
        sleep(0.5)

        ###############################################################################################

        ##############################################################################################
        # ******Test Negative FLT12 Fault******
        ##############################################################################################
        self.psu.toggle_output("2", "OFF")
        sleep(1)
        self.psu.toggle_output("3", "OFF")
        sleep(1)

        self.init_psu()
        flt12_flag = False  # FLT12 Status Flag Initializaiton
        self.gen.apply_pulse("1", self.GEN_TEST_FREQ, "0.005", self.GEN_TEST_VOLTAGE, "0")
        sleep(1)
        flt12_negative_assert_pin_voltage = round(self.dmm.meas_dcv(), 4)  # Create a valid initial \
        # value for the while loop...
        self.psu.set_voltage("3", "10")  # Drop PSU N15V to 10V to expedite testing...
        sleep(1)
        N15V_setpoint = self.psu.measure_voltage("3")
        psu_rb = N15V_setpoint  # Initialize psu_rb before the loop print statements...
        sleep(1)
        while ((flt12_negative_assert_pin_voltage >= self.FLT12_ASSERT) and (abs(N15V_setpoint)
                                                                             >= self.N15V_THRES_LOW)):
            # Repeat until fault is asserted...
            flt12_negative_assert_pin_voltage = round(self.dmm.meas_dcv(), 4)
            sleep(1)
            print(f"PSU N15V Rail Voltage: {psu_rb} \n"
                  f"FLT12 Fault Status Voltage:{np.round(flt12_negative_assert_pin_voltage, 3)} \n"
                  f"FLT12 Fault Status Flag: {flt12_flag}")
            # input(f"pre-sp increase... 249....{N15V_setpoint}")
            N15V_setpoint += 0.250
            # input(f"Post-sp increase...{N15V_setpoint}")
            psu_rb = self.psu.measure_voltage("3")
            sleep(1)
            # input(f"while ({N15V_setpoint - 0.02}) <= {psu_rb} <= ({N15V_setpoint + 0.02})")
            while not ((N15V_setpoint - 0.02) <= psu_rb <= (N15V_setpoint + 0.02)): \
                    # Command PSU to drop 250mV until readback shows it does...
                print("Adjusting PSU voltage...retrying...")
                psu_sp = str(N15V_setpoint)
                print(f"DBUG PSU SP: {psu_sp}")
                self.psu.set_voltage("3", psu_sp)
                sleep(1)
                psu_rb = self.psu.measure_voltage("3")
                sleep(1)
                # input(f"PSU RB 260: {psu_rb}")
            print("PSU Voltage adjusted, re-acquiring data...")

        # Fell out of the loop...FLT12 is now ASSERTED...
        # input(f"DBUG: 267: fell out of while cond. (({flt12_assert_pin_voltage[4]} \
        # >= {FLT12_DEASSERT}) and ({abs(N15V_setpoint)} >= {N15V_THRES_HIGH})):")
        flt12_flag = True
        flt12_negative_assert_ps_voltage = psu_rb  # Store the final value that caused assert

        print(f"PSU N15V Rail Voltage: {psu_rb} \n"
              f"FLT12 Fault Status Voltage: {flt12_negative_assert_pin_voltage} \n"
              f"FLT12 Fault Status Flag: {flt12_flag}\n\n\n")
        sleep(0.5)
        if ((flt12_flag is True) and (abs(psu_rb) >= self.N15V_THRES_LOW) and (abs(psu_rb) <= self.N15V_THRES_HIGH)):
            print("FLT12 Negative Assertion Test passed!\n")
            flt12_negative_assertion_test_passed = True
        else:
            print("FLT12 Negative Assertion Test failed: N15V is outside threshold!\n")
            flt12_negative_assertion_test_passed = False
        self.psu.toggle_output("2", "OFF")
        sleep(0.5)
        self.psu.toggle_output("3", "OFF")
        sleep(0.5)
        self.psu.set_voltage(chan="2", val="15")
        sleep(0.5)
        self.psu.set_voltage(chan="3", val="15")
        sleep(0.5)

        print("FLT12 Fault Test is complete. \n")

        test_passed = (flt12_positive_assertion_test_passed and flt12_deassertion_test_passed and
                       flt12_negative_assertion_test_passed)
        # input(f"BLOCKING Passing returns out...Positive assert pin voltage: {flt12_positive_assert_pin_voltage}")
        # input(f"BLOCKING Passing returns out...Negative assert pin voltage: {flt12_negative_assert_pin_voltage}")
        return {
            "test_passed": test_passed,
            "positive_assertion_test": flt12_positive_assertion_test_passed,
            "deassertion_test": flt12_deassertion_test_passed,
            "initial_voltage": self.flt12_initial_voltage,
            "positive_assert_pin_voltage": flt12_positive_assert_pin_voltage,
            "positive_assert_ps_voltage": flt12_positive_assert_ps_voltage,
            "negative_assertion_test": flt12_negative_assertion_test_passed,
            "negative_assert_pin_voltage": flt12_negative_assert_pin_voltage,
            "negative_assert_ps_voltage": flt12_negative_assert_ps_voltage,
            "test_current": self.GEN_TEST_VOLTAGE
        }


if __name__ == "__main__":
    from instrument_modules.rigol_dp800 import DP800
    PSU_IP_ADDRESS = "10.0.142.1"
    psu_standalone = DP800(connection_method="IP", address=PSU_IP_ADDRESS)
