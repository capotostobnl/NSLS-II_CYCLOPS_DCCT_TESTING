"""This module handles plot generation from decoded waveform binaries,
and performs calculations on the data acquired.

M. Capotosto
3/9/2025
NSLS-II Diagnostics and Instrumentation"""
import os
from struct import unpack
import numpy as np
import matplotlib.pyplot as plt

#############################################################################
# ******PASS/FAIL THRESHOLDS******
#############################################################################
MAX_DC_OFFSET = 0.010  # Maximum DC Offset in waveform
MAX_PK_PK = 0.6  # Maximum measured PK-to-PK Voltage
MIN_PK_PK = 0.5  # Minimum measured PK-to-PK Voltage

#############################################################################

# Initialize plots...


def init_plots():
    """Initialize plots"""
    # Create a plot figure with 4 plots, for CHA, CHB, CHC, CH AB.
    f, ax = plt.subplots(2, 2)
    f.set_figheight(12)
    f.set_figwidth(12)
    f.suptitle("ALSu DCCT Test Data")
    return f, ax


def clear_plots(ax):
    """Clear old data off plots..."""
    ax[0, 0].clear()
    ax[1, 0].clear()
    ax[0, 1].clear()
    ax[1, 1].clear()


def calculate_frequency(volts):
    """Calculate the frequency of the waveform using Fourier Transform"""

    fs = 2000
    N = len(volts[1])  # Number of samples # pylint: disable=C0103
    # dt = scope_time[1] - scope_time[0]  # Time interval between samples
    dt = 1 / fs
    # Perform the Fast Fourier Transform (FFT) on the signal
    # (assuming volts[1] is the waveform of interest)
    fft_result = np.fft.fft(volts[1])

    # Frequency values corresponding to the FFT result
    freqs = np.fft.fftfreq(N, dt)

    # Only take the positive frequencies
    positive_freqs = freqs[:N // 2]
    positive_fft_result = np.abs(fft_result[:N // 2])

    # Find the peak frequency (index of the maximum FFT result)
    peak_freq_idx = np.argmax(positive_fft_result)
    peak_frequency = positive_freqs[peak_freq_idx]  # Peak frequency in Hz

    return peak_frequency


def calculate_phase_shift(volts):
    """Calculate the phase shift between CH1 and CH2 Waveforms using FFT"""
    # Calculate the frequency of the signal using FFT
    frequency = calculate_frequency(volts)

    # Perform FFT on both Channel 1 and Channel 2 signals
    fft_ch1 = np.fft.fft(volts[1])
    fft_ch2 = np.fft.fft(volts[2])

    # Get the index corresponding to the peak frequency
    # (same frequency for both channels)
    N = len(volts[1])  # pylint: disable=C0103
    # dt = scope_time[1] - scope_time[0]
    # freqs = np.fft.fftfreq(N, dt)
    # positive_freqs = freqs[:N // 2]

    # Find the index of the peak frequency
    peak_freq_idx = np.argmax(np.abs(fft_ch1[:N // 2]))
    # Use Channel 1 to find the peak frequency index

    # Find the phase at the peak frequency
    phase_ch1 = np.angle(fft_ch1[peak_freq_idx])
    phase_ch2 = np.angle(fft_ch2[peak_freq_idx])

    # Calculate the phase shift in degrees
    phase_shift = np.degrees(phase_ch2 - phase_ch1)  # Phase shift between
    # Channel 2 and Channel 1
    if phase_shift < 0:
        phase_shift += 360  # Ensure phase is
        # positive and in the range [0, 360)

    return frequency, phase_shift


def unpack_raw_adc(channel_data, decoded_wfdata):
    """Unpack the ADC waveform data, convert ADC values to voltages,
    and find the min/max voltages"""
    volts = {}
    ymax = {}
    ymin = {}

    for i in range(1, 4):  # Loop over channels 1 to 4
        adc_wave = np.array(unpack(f"{len(decoded_wfdata[i]['adc_wave'])}B",
                                   decoded_wfdata[i]['adc_wave']))

        volts[i] = (adc_wave - channel_data[i]["yoff"]) *\
            channel_data[i]["ymult"] + channel_data[i]["yzero"]
        ymax[i] = max(volts[i])
        ymin[i] = min(volts[i])

    scope_time = np.arange(0, len(volts[1]), 1)  # Only one scope_time is used, so choose CH1

    return volts, ymax, ymin, scope_time


def plot_waveforms(channel_data, decoded_wfdata, plot_filename):
    """Generate four plots with waveforms and additional info."""
    # Initialize all return variables
    ch1_threshold = ch2_threshold = ch3_threshold = False
    freq_phase_pass = False
    vpp1 = vpp2 = vpp3 = 0
    frequency = phase_shift = 0
    f, ax = init_plots()
    clear_plots(ax)
    volts, ymax, ymin, scope_time = unpack_raw_adc(channel_data, decoded_wfdata)

    # Plot Channel 1
    ax[0, 0].plot(scope_time, volts[1], label="Channel 1")
    ax[0, 0].set_title("Channel 1, IOUT 1")
    ax[0, 0].grid(True)
    ax[0, 0].text(0.05, 0.9, f"Peak-to-Peak: {round(ymax[1] - ymin[1], 3)} V",
                  transform=ax[0, 0].transAxes, fontsize=14, verticalalignment='top',
                  bbox={'facecolor': 'wheat', 'alpha': 0.7})
    vpp = ymax[1] - ymin[1]
    vpp1 = ymax[1] - ymin[1]
    if 0.50 <= vpp <= 0.54:  # Set Pass/Fail Tolerance
        ax[0, 0].set_facecolor((0, 1, 0, 0.2))  # Green with 50% alpha
        ch1_threshold = True
    else:
        ax[0, 0].set_facecolor((1, 0, 0, 0.2))  # Red with 50% alpha
        ch1_threshold = False

    # Plot Channel 2
    ax[0, 1].plot(scope_time, volts[2], label="Channel 2")
    ax[0, 1].set_title("Channel 2, IOUT 2")
    ax[0, 1].grid(True)
    ax[0, 1].text(0.05, 0.9, f"Peak-to-Peak: {round(ymax[2] - ymin[2], 3)} V",
                  transform=ax[0, 1].transAxes, fontsize=14, verticalalignment='top',
                  bbox=dict(facecolor='wheat', alpha=0.7))
    vpp = ymax[2] - ymin[2]  # Set Pass/Fail Tolerance
    vpp2 = ymax[2] - ymin[2]
    if 0.50 <= vpp <= 0.54:
        ax[0, 1].set_facecolor((0, 1, 0, 0.2))  # Green with 50% alpha
        ch2_threshold = True
    else:
        ax[0, 1].set_facecolor((1, 0, 0, 0.2))  # Red with 50% alpha
        ch2_threshold = False

    # Plot Channel 3
    ax[1, 0].plot(scope_time, volts[3], label="Channel 3")
    ax[1, 0].set_title("Channel 3, SIGNAL GEN")
    ax[1, 0].grid(True)
    ax[1, 0].text(0.05, 0.9, f"Peak-to-Peak: {round(ymax[3] - ymin[3], 3)} V",
                  transform=ax[1, 0].transAxes, fontsize=14, verticalalignment='top',
                  bbox={'facecolor': 'wheat', 'alpha': 0.7})
    vpp = ymax[3] - ymin[3]  # Set Pass/Fail Tolerance
    vpp3 = ymax[3] - ymin[3]
    if 20 <= vpp <= 22:
        ax[1, 0].set_facecolor((0, 1, 0, 0.2))  # Green with 50% alpha
        ch3_threshold = True
    else:
        ax[1, 0].set_facecolor((1, 0, 0, 0.2))  # Red with 50% alpha
        ch3_threshold = False

    # Calculate Phase Shift between Channel 1 and Channel 2
    frequency, phase_shift = calculate_phase_shift(volts)

    # Plot Channel 1 and Channel 2 (Phase Shift)
    ax[1, 1].plot(scope_time, volts[1], label="Channel 1")
    ax[1, 1].plot(scope_time, volts[2], label="Channel 2")
    ax[1, 1].set_title("Channel 1 & Channel 2 (IOUT 1 and IOUT 2) Phase Shift")
    ax[1, 1].grid(True)
    phase_shift = round(phase_shift, 2)
    frequency = round(frequency, 2)
    ax[1, 1].text(0.05, 0.9, f"Phase Shift: {phase_shift}°\nFrequency:"
                  f"{frequency} Hz",
                  transform=ax[1, 1].transAxes, fontsize=14, verticalalignment='top',
                  bbox={'facecolor': 'wheat', 'alpha': 0.7})
    if 9 <= frequency <= 11 and 178 <= phase_shift <= 181:   # Set Pass/Fail Tolerance
        ax[1, 1].set_facecolor((0, 1, 0, 0.2))  # Green with 50% alpha
        freq_phase_pass = True
    else:
        ax[1, 1].set_facecolor((1, 0, 0, 0.2))  # Red with 50% alpha
        freq_phase_pass = False

    f.savefig(plot_filename, bbox_inches='tight')
    # Saves the figure with tight bounding box

    plt.tight_layout()
    plt.show()
    return plot_filename, ch1_threshold, ch2_threshold, ch3_threshold, \
        frequency, phase_shift, freq_phase_pass, vpp1, vpp2, vpp3


if __name__ == "__main__":
    # Dummy test data
    from datetime import datetime
    dir_create_time = datetime.now()
    dir_time_formatted = dir_create_time.strftime("%m-%d-%y_%H-%M-%S")
    DCCT_SN_L = 4206969
    raw_data_path = f"./Test_Data/DCCT_{DCCT_SN_L}-{dir_time_formatted}/raw_data"  # pylint: disable=C0103
    os.makedirs(raw_data_path, exist_ok=True)
    plot_filename_l = os.path.join(raw_data_path, f"waveform_plots_{DCCT_SN_L}_"
                                   f"{dir_time_formatted}.png")
    #  Sampling parameters
    fs_l = 2000  # Sampling frequency (Hz)  # pylint: disable=C0103
    duration = 1  # pylint: # pylint: disable=C0103
    t = np.linspace(0, duration, fs_l, endpoint=False)  # Time array

    # Generate 10 Hz, 1V peak-to-peak sine waves
    sine_wave_1 = 0.5 * np.sin(2 * np.pi * 10 * t)  # CH1: 10Hz, 1Vpp (0.5V amplitude)
    sine_wave_2 = -sine_wave_1  # CH2: 180-degree phase shift (inverted CH1)
    sine_wave_3 = sine_wave_1  # CH3: Same as CH1 (no shift)

    # Simulated ADC conversion (assuming 8-bit unsigned ADC, 0-255 range)
    adc_max = 255  # pylint: disable=C0103
    sine_wave_1_adc = ((sine_wave_1 + 0.5) * adc_max).astype(np.uint8)
    sine_wave_2_adc = ((sine_wave_2 + 0.5) * adc_max).astype(np.uint8)
    sine_wave_3_adc = ((sine_wave_3 + 0.5) * adc_max).astype(np.uint8)

    # Test channel data (simulate oscilloscope scaling factors)
    test_channel_data = {
        1: {"yoff": 128, "ymult": 1 / 255, "yzero": 0, "xincr": 1 / fs_l},
        2: {"yoff": 128, "ymult": 1 / 255, "yzero": 0, "xincr": 1 / fs_l},
        3: {"yoff": 128, "ymult": 1 / 255, "yzero": 0, "xincr": 1 / fs_l},
    }

    # Encapsulating ADC waveforms in a format similar to real oscilloscope data
    test_decoded_wfdata = {
        1: {"headerlen": 2, "header": b"\x00\x01", "adc_wave": sine_wave_1_adc.tobytes()},
        2: {"headerlen": 2, "header": b"\x00\x01", "adc_wave": sine_wave_2_adc.tobytes()},
        3: {"headerlen": 2, "header": b"\x00\x01", "adc_wave": sine_wave_3_adc.tobytes()},
    }

    plot_waveforms(test_channel_data, test_decoded_wfdata, plot_filename_l)  # Now works correctly!

    input()

    plot_waveforms(test_channel_data, test_decoded_wfdata, plot_filename_l)  # Now works correctly!
