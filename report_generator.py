# flake8: noqa E501
"""This module manages ReportLab Report Generation

M. Capotosto
3/5/2025
NSLS-II Diagnostics and Instrumentation
"""
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, \
    Paragraph, Image, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color
from reportlab.lib import colors


PAGE_WIDTH, PAGE_HEIGHT = letter  # Page size!
styles = getSampleStyleSheet()


def plot_pdf(dut_info, report_path, plot_path):
    """Generate the PDF using data from the dictionary and save it to the
    provided report path."""
    # Create the document object
    print(report_path)
    doc = SimpleDocTemplate(report_path, pagesize=letter)

    # Create a Story list to hold the content
    Story = []
#############################################################################
# ******Paragraph Styles******
#############################################################################
    # Define the title style (24pt font, centered)
    title_style = ParagraphStyle(
        "TitleStyle",
        fontName="Helvetica-Bold",  # Font name
        fontSize=18,                # Font size
        alignment=1,                # Center the title
        spaceAfter=12               # Space after the title
    )

    # Define the Name Subheading Style
    name_style = ParagraphStyle(
        "NameStyle",
        fontName="Helvetica-Bold",  # Font name
        fontSize=12,                # Font size
        alignment=0,                # Center the title
        leading=12,               # Line spacing on CR
        spaceAfter=12               # Space after the title
    )

    # Title style for the table (size 14, left-aligned)
    table_title_style = ParagraphStyle(
        "TableTitleStyle",
        fontName="Helvetica",
        fontSize=14,
        alignment=1,  # Centered
        spaceAfter=6,
        textColor=colors.black
    )

    # Create a custom style for bold and colored text
    bold_green = ParagraphStyle(
        "BoldGreen",
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=0,
        spaceAfter=6,
        textColor=colors.green,
    )

    bold_red = ParagraphStyle(
        "BoldRed",
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=0,
        spaceAfter=6,
        textColor=colors.red,
    )
#############################################################################
    #############################################################################
    # ******Calculate overall_test_passfail Before Report Generation******
    #############################################################################

    #############################################################################
    # ******FLT12 Fault 1 and 2 Test Results******
    #############################################################################
    # Define threshold values for voltage comparison
    INIT_THRESHOLD_VOLTAGE = 14.3  # Change this as needed
    FAULT_THRESHOLD_VOLTAGE = 1


    # Extract voltage values, ensuring they are floats
    flt12_initial_voltage = float(dut_info["flt12_initial_voltage_l"])
    flt12_positive_signal_voltage = float(
         dut_info["flt12_positive_signal_voltage_l"])
    flt12_negative_signal_voltage = float(
         dut_info["flt12_negative_signal_voltage_l"])
    # Dictionary containing test names, values, and pass/fail results
    # print(dut_info)

    flt12_tests_results = {
        "FLT12 Overall Testing": dut_info['flt12_test_passed_l'],
        "FLT12 Positive Assertion": dut_info['flt12_positive_assertion_test_passed_l'],
        "FLT12 Negative Assertion": dut_info['flt12_negative_assertion_test_passed_l'],
        "FLT12 De-Assertion": dut_info['flt12_deassertion_test_passed_l'],
        "FLT12 Initial Voltage": (flt12_initial_voltage, flt12_initial_voltage >= INIT_THRESHOLD_VOLTAGE),
        "FLT12 Positive Fault Voltage": (flt12_positive_signal_voltage, (flt12_positive_signal_voltage
                                         <= FAULT_THRESHOLD_VOLTAGE)),
        "FLT12 Negative Fault Voltage": (flt12_negative_signal_voltage, (flt12_negative_signal_voltage
                                         <= FAULT_THRESHOLD_VOLTAGE))
    }
    #############################################################################
    # ******Add Current Test Values******
    #############################################################################

    degree_sign = '\N{DEGREE SIGN}'
    freq_phase = f"{dut_info['current_test_frequency']} Hz, {dut_info['current_test_phase_shift']}{degree_sign}"
    current_tests_results = {
        # "Current Overall Testing": ,
        "CT Measurement Overall Testing": (dut_info['current_test_freq_phase_pass'] 
                                           and dut_info['current_test_ch1_threshold']
                                           and dut_info['current_test_ch2_threshold']
                                           and dut_info['current_test_ch3_threshold']),
        "Channel 1 Voltage Threshold": (f"{dut_info['current_test_vpp1']}Vpp", dut_info['current_test_ch1_threshold']),
        "Channel 2 Voltage Threshold": (f"{dut_info['current_test_vpp2']}Vpp", dut_info['current_test_ch2_threshold']),
        "Channel 3 Voltage Threshold": (f"{dut_info['current_test_vpp3']}Vpp", dut_info['current_test_ch3_threshold']),
        "Frequency and Phase": (freq_phase, dut_info['current_test_freq_phase_pass']),
    }

    overall_test_passfail = (flt12_tests_results["FLT12 Overall Testing"] and current_tests_results["CT Measurement Overall Testing"])


#############################################################################
# ******Titles and Subheadings******
#############################################################################
    # Create the title paragraph
    title = Paragraph(dut_info["Title"], title_style)

    # Add title to the story
    Story.append(title)

    # Add space after the title
    Story.append(Spacer(1, 0.3*inch))  # Adds space after title

    # Add Pass/Fail Status
    if overall_test_passfail:
        Story.append(Paragraph("Overall Test Status: Passed!", bold_green))
    else: 
        Story.append(Paragraph("Overall Test Status: Failed!", bold_red))
    # Add other details (Technician, Life, Date, Time)
    Story.append(Paragraph(f"Technician: {dut_info['Technician']}, \
                           Life #: {dut_info['Life']}", name_style))
    Story.append(Paragraph(f"Test performed: {dut_info['Date']}, \
                            {dut_info['Time']}", name_style))
    Story.append(Paragraph(f"Raw Serial Number/Sticker Data: {dut_info['dcct_sn_raw']}"))


#############################################################################






# Add space before the table title
    Story.append(Spacer(1, 18))

    # Add the table title
    table_title = Paragraph("FLT12 Fault Signal 1 and 2 Test Results",
                            table_title_style)
    Story.append(table_title)

    # Add space after the table title
    Story.append(Spacer(1, 12))

    # Prepare table data with headers
    flt12_data = [["Test", "Value", "Status"]]

    # Populate the table with test results
    for test_name, result in flt12_tests_results.items():
        if isinstance(result, tuple):  # Voltage values
            value_str = f"{result[0]:.2f} V"
            status_str = "Pass" if result[1] else "Fail"
        else:  # Boolean test results
            value_str = "N/A"
            status_str = "Pass" if result else "Fail"

        flt12_data.append([test_name, value_str, status_str])

    # Create the Table
    table = Table(flt12_data)

    # Style the table
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header bg color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center text
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
        ('BACKGROUND', (1, 1), (-1, -1), colors.white),  # Default row bg
    ]))

    # Define colors with transparency
    red = Color(1, 0, 0, alpha=0.5)  # Red (Fail)
    green = Color(0, 1, 0, alpha=0.5)  # Green (Pass)

    # Apply row colors based on Pass/Fail status
    for row_idx, row in enumerate(flt12_data[1:], start=1):  # Skip header
        status = row[2]  # Get "Status" value
        if status == "Fail":
            table.setStyle(TableStyle([('BACKGROUND',
                                        (0, row_idx), (-1, row_idx), red)]))
        elif status == "Pass":
            table.setStyle(TableStyle([('BACKGROUND',
                                        (0, row_idx), (-1, row_idx), green)]))

    # Add the table to the story
    Story.append(table)

    Story.append(Spacer(1, 0.3*inch))  # Adds space after table
    Story.append(Paragraph("Pass/Fail Threshold Voltage for FLT12 Initial "
                           f"Voltage: >{INIT_THRESHOLD_VOLTAGE}V"))
    Story.append(Paragraph("Pass/Fail Threshold Voltage for FLT12 Fault "
                           f"Voltage: <{FAULT_THRESHOLD_VOLTAGE}V"))
    Story.append(Paragraph("FLT12 Fault testing carried out with +/-"
                           f"{dut_info['flt12_test_current']}A current through DCCT"))
    Story.append(Spacer(1, 0.5*inch))  # Adds space after table
    Story.append(Paragraph("Test Current for IOUT Measurement: +/-10A"
                           " at 10Hz Sinusoidal"))
    Story.append(Paragraph("(20Vpp sine into Kepco current control input)"))

#############################################################################
# ******Add Current Test Tables******
#############################################################################

    degree_sign = '\N{DEGREE SIGN}'
    freq_phase = f"{dut_info['current_test_frequency']} Hz, {dut_info['current_test_phase_shift']}{degree_sign}"
    current_tests_results = {
        # "Current Overall Testing": ,
        "CT Measurement Overall Testing": (dut_info['current_test_freq_phase_pass'] 
                                           and dut_info['current_test_ch1_threshold']
                                           and dut_info['current_test_ch2_threshold']
                                           and dut_info['current_test_ch3_threshold']),
        "Channel 1 Voltage Threshold": (f"{dut_info['current_test_vpp1']}Vpp", dut_info['current_test_ch1_threshold']),
        "Channel 2 Voltage Threshold": (f"{dut_info['current_test_vpp2']}Vpp", dut_info['current_test_ch2_threshold']),
        "Channel 3 Voltage Threshold": (f"{dut_info['current_test_vpp3']}Vpp", dut_info['current_test_ch3_threshold']),
        "Frequency and Phase": (freq_phase, dut_info['current_test_freq_phase_pass']),
    }

    # Add space before the table title
    Story.append(Spacer(1, 18))

    # Add the table title
    table_title = Paragraph("Sinusoidal Current Test Results",
                            table_title_style)
    Story.append(table_title)

    # Add space after the table title
    Story.append(Spacer(1, 12))

    # Prepare table data with headers
    current_data = [["Test", "Value", "Status"]]

    # Populate the table with test results
    for test_name, result in current_tests_results.items():
        if isinstance(result, tuple):  # Not pass/fail values
            value_str = result[0]
            status_str = "Pass" if result[1] else "Fail"
        else:  # Boolean test results
            value_str = "N/A"
            status_str = "Pass" if result else "Fail"

        current_data.append([test_name, value_str, status_str])

    # Create the Table
    table = Table(current_data)

    # Style the table
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header bg color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center text
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
        ('BACKGROUND', (1, 1), (-1, -1), colors.white),  # Default row bg
    ]))

    # Define colors with transparency
    red = Color(1, 0, 0, alpha=0.5)  # Red (Fail)
    green = Color(0, 1, 0, alpha=0.5)  # Green (Pass)

    # Apply row colors based on Pass/Fail status
    for row_idx, row in enumerate(current_data[1:], start=1):  # Skip header
        status = row[2]  # Get "Status" value
        if status == "Fail":
            table.setStyle(TableStyle([('BACKGROUND',
                                        (0, row_idx), (-1, row_idx), red)]))
        elif status == "Pass":
            table.setStyle(TableStyle([('BACKGROUND',
                                        (0, row_idx), (-1, row_idx), green)]))

    # Add the table to the story
    Story.append(table)


#############################################################################
# ******Add Current Test Plots and Data******
#############################################################################
    width_in_inches = 1012 / 130  # Scale image maintaining A/R
    height_in_inches = 1087 / 130  # by changing divisor

    Story.append(PageBreak())
    plot_title = Paragraph("Current Test Waveforms",
                           table_title_style)
    # Add space after the title
    Story.append(Spacer(1, 0.125*inch))  # Adds space after title
    Story.append(plot_title)

    img = Image(plot_path, width=width_in_inches * inch,
                height=height_in_inches * inch)
    img.hAlign = 'CENTER'  # Center the image
    Story.append(img)
#############################################################################

#############################################################################
# ******Build the PDF******
#############################################################################
    # Build the document (this automatically handles page creation)
    doc.build(Story)
#############################################################################


if __name__ == "__main__":
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    plot_path_l = os.path.join(current_dir, "testplot.png")
    # Example dut_info dictionary with sample values
    dut_info_l = {
        "Title": "DCCT Test Results for DCCT S/N: $dcct_sn",
        "Technician": "$Technician",
        "Life": "$tester_life",
        "Date": "$report_date_formatted",
        "Time": "$report_time_formatted",
        "flt12_test_passed_l": True,
        "flt12_positive_assertion_test_passed_l": True,
        "flt12_negative_assertion_test_passed_l": False,
        "flt12_deassertion_test_passed_l": True,
        "flt12_initial_voltage_l": 14.8,
        "flt12_positive_signal_voltage_l": 8.02,
        "flt12_negative_signal_voltage_l": 8.125,
        "flt12_positive_psu_voltage_l": -6,
        "flt12_negative_psu_voltage_l": -5,
        "dcct_sn_raw": "DCCT-M-B-0011-70000000006-BZ20130002-HBA20030148 \
                       -22211030016-BZ22020423-HBA22170043-CTP-6303-50-A"

        }

    report_path_l = "sample_test_report.pdf"
    plot_pdf(dut_info_l, report_path_l, plot_path_l)
