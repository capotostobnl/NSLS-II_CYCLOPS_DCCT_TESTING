"""This module configures the VISA Utilities,
and sets up a resource manager instantiation to be used in other modules.

M. Capotosto
3/4/2025
NSLS-II Diagnostics and Instrumentation
"""

import pyvisa
from pyvisa import VisaIOError


def get_resource_manager():
    """Return a PyVISA resource manager instance."""
    return pyvisa.ResourceManager()


def connect_usb_instrument(address):
    """
    connect USB instrument based on the
    given identifier.
    Returns (device, address, status) tuple.
    """
    rm = get_resource_manager()

    try:
        device = rm.open_resource(address)
        return device, address, "Connected"
    except VisaIOError:
        return None, None, "Not Connected"


def connect_ethernet_instrument(ip_address, port=5025, use_socket=False):
    """
    Connect to an Ethernet-based instrument using its IP address.

    Parameters:
        ip_address (str): The instrument's IP address.
        port (int): The port number (default: 5025 for SCPI over raw socket).
        use_socket (bool): Whether to use raw socket communication.

        VXI-11 (TCPIP0::<IP>::INSTR) --> use_socket=False
        HiSLIP (TCPIP0::<IP>::hislip0) --> use_socket=False
        Raw Socket (TCPIP0::<IP>::5025::SOCKET) --> use_socket=True

    Returns:
        device (pyvisa.Resource): The VISA instrument resource.
        address (str): The VISA resource string used.
        status (str): Connection status.
    """
    rm = get_resource_manager()

    if use_socket:
        resource_str = f"TCPIP0::{ip_address}::{port}::SOCKET"
    else:
        resource_str = f"TCPIP0::{ip_address}::INSTR"  # VISA over Ethernet

    try:
        device = rm.open_resource(resource_str)
        return device, resource_str, "Connected"
    except VisaIOError:
        return None, None, "Not Connected"


def list_instruments():
    """List all available instruments on the network."""
    rm = get_resource_manager()
    instruments = rm.list_resources()

    if instruments:
        print("Available Instruments:")
        for inst in instruments:
            print(f" - {inst}")
            try:
                # Open the instrument resource
                device = rm.open_resource(inst)
                # Send the *IDN? query and get the response
                idn_response = device.query("*IDN?").strip()
                # Split the response by commas and display with titles
                idn_parts = idn_response.split(",")
                if len(idn_parts) == 4:
                    print(f"   Manufacturer: {idn_parts[0]}")
                    print(f"   Model: {idn_parts[1]}")
                    print(f"   Serial Number: {idn_parts[2]}")
                    print(f"   Firmware Version: {idn_parts[3]}")
                else:
                    print("   Unrecognized IDN format.")
            except pyvisa.VisaIOError as e:
                print(f"   Error communicating with {inst}: {e}")
    else:
        print("No instruments found.")


if __name__ == "__main__":
    print("Scanning for available instruments...")
    list_instruments()
