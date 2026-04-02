# ALSu DCCT Test Setup & Procedure Checklist

This checklist guides the technician through the physical setup, instrument configuration, and software execution required to test the ALSu DCCT modules.

## 1. Pre-Test Preparation
- [ ] The testing laptop is connected to the local instrument network (ensure IPs `10.0.142.x` and `10.0.143.x` are reachable).
- [ ] The Python virtual environment is activated.
- [ ] Required packages from `requirements.txt` are installed.

## 2. Hardware Power-Up
Ensure all laboratory instruments are turned ON:
- [ ] Kepco Power Supply
- [ ] Rigol DP800 Series Power Supply
- [ ] Rigol DG4000 Series Signal Generator
- [ ] Tektronix DPO4000/MSO4000 Series Oscilloscope
- [ ] Keysight 34461A or Keithley 2100 Digital Multimeter (DMM)
- [ ] Differential Probes for Oscilloscope

## 3. Physical Connections & Wiring
- [ ] **GRAY** CT conductors are routed and secured to the **GRAY** terminal blocks.
- [ ] **BLUE** conductors are routed and secured to the **BLUE** terminal blocks.
- [ ] Conductors loop through the DCCT only once, and wire is at least 2" away from rear of DCCT Chassis (Past the yellow spacer sticks)

## 4. Manual Instrument Configuration
While the script handles most parameters, the following must be set manually prior to execution:
- [ ] **Kepco PSU Front Panel Configuration**:
  - [ ] VOLTAGE CONTROL Switch: **OFF**
  - [ ] CURRENT CONTROL Switch: **OFF**
  - [ ] *Note: MODE Switch and Potentiometer positions do not matter.*
- [ ] **Oscilloscope Probes**:
  - [ ] Differential probes are powered **ON**.
  - [ ] Differential probes are physically set to **x20 Attenuation**.

## 5. Software Execution
- [ ] Open a terminal/command prompt and run: `python main.py`.
- [ ] When prompted, enter your **Name** and confirm.
- [ ] When prompted, enter your **Life #** and confirm.
- [ ] Scan or manually enter the **DCCT Serial Number** (the script will capture the first 13 characters) and confirm.
- [ ] Acknowledge the on-screen connection confirmation prompts by pressing `Return`.

## 6. Testing & Review
- [ ] Allow the script to initialize the instruments and run the **FLT12 Fault 1 & 2 Tests**.
- [ ] If FLT12 tests fail, select whether to retry, restart with a new unit, or proceed to the next step.
- [ ] Allow the script to run the **DCCT Current Tests** (Phase, Frequency, and Voltage validation).
- [ ] Once completed, verify that the automated **PDF Test Report** opens on your screen.
- [ ] Verify that raw `.csv` and `.png` plot data were successfully saved in the new `Test_Data/DCCT_<SN>-<Timestamp>/raw_data/` directory.
- [ ] Affix a Green or Red 'QA' sticker to indicate the unit's pass or fail status
- [ ] Print reports as needed, and upload to Git repository at end of shift for archival