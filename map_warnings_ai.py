# This code will do the following:
# 1) Take a pdf file name, "G1.pdf" and utilitytype = 'Gas', INPUT
# 2) Convert the pdf into jpg and crop the map area
# 3) Detect High Pressure Lines using thresholding and print a warning, OUTPUT

# REMOVE THE NEGATIVE WARNINGS
# FIND FILE NAMES WITH CERTAIN PREFIX G*.pdf

# -------------------------- xxx ------------------------------------------------------


# All required imports
import cv2
import numpy as np
import pdfbox
import sys
import argparse
import json
import os

# -------------------------- xxx ------------------------------------------------------
# Argument Parser

# import argparse
#
# ap = argparse.ArgumentParser()
#
# ap.add_argument("-u", "--utility_type", required=True,
#                 help="name of the utility")
# ap.add_argument("-f", "--filename_pdf", required=True,
#                 help="name of the PDF file, eg. G1.pdf")
# ap.add_argument("-r", "--rootdir", required=True,
#                 help="root directory name, eg. .")
#
# args = vars(ap.parse_args())
#
# filename_pdf = args["filename_pdf"]
# utility_type = args["utility_type"]
# Root_directory_name = args["rootdir"]

# -------------------------- xxx ------------------------------------------------------
# filter threshold values and warnings
# For Gas Maps

# Skyblue: MP MAINS Gas Lines
low_GAS_MP = np.array([80, 100, 20])
high_GAS_MP = np.array([110, 255, 255])

# warnings- positive and negative
warning_p_GAS_MP = 'Warning: There is a Medium Pressure Gas Line in this Area| '
# warning_n_GAS_MP = 'There are no High Pressure Gas Lines in this Area| '
warning_n_GAS_MP = ''

# threshold for detection
z_thresh_MP = 220

# -------------------------- xxx ------------------------------------------------------


# Orange: LHP MAINS Gas Lines
low_GAS_LHP = np.array([10, 150, 20])
high_GAS_LHP = np.array([20, 255, 255])

# warnings- positive and negative
warning_p_GAS_LHP = 'Warning: There is an LHP Pressure Gas Line in this Area | '
# warning_n_GAS_LHP = 'There are no LHP Pressure Gas Lines in this Area| '
warning_n_GAS_LHP = ''

# threshold for detection
z_thresh_LHP = 40

# -------------------------- xxx ------------------------------------------------------


# Green: IP MAINS Gas Lines
low_GAS_IP = np.array([50, 100, 20])
high_GAS_IP = np.array([65, 255, 255])

# warnings- positive and negative
warning_p_GAS_IP = 'Warning: There is an Intermediate Pressure Gas Line in this Area | '
# warning_n_GAS_IP = 'There are no Intermediate Pressure Gas Lines in this Area| '
warning_n_GAS_IP = ''

# threshold for detection
z_thresh_IP = 150

# -------------------------- xxx ------------------------------------------------------


# For Electricity maps


# filter threshold values
# Green: HV Electricity Lines
low_ELEC_HV = np.array([50, 100, 20])
high_ELEC_HV = np.array([65, 255, 255])

# warnings- positive and negative
warning_p_ELEC_HV = 'Warning: There is a High Voltage Electricity Line in this Area | '
# warning_n_ELEC_HV = 'There are no High Voltage Electricity Lines in this Area | '
warning_n_ELEC_HV = ''

# threshold for detection
z_thresh_HV = 280


# -------------------------- xxx ------------------------------------------------------


# Function to do the thresholding operation for detection
# Inputs:# hsv_img -  image converted to HSV
# img - original image
# z - the threshold countNonZero value for a negative example(pixels in legend)
# low_mask, high_mask - filter range values
# warnings_p, warning_n - warnings for positive and negative detection
# Outputs: #

def threshold_filter(img, hsv_img, z_thresh, low_mask, high_mask, warning_p, warning_n):
    # Do threshoding detection
    color_mask = cv2.inRange(hsv_img, low_mask, high_mask)
    color_det = cv2.bitwise_and(img, img, mask=color_mask)

    # # Read the image in greyscale, count detected pixels
    img_grey = color_det[:, :, -1]
    z = cv2.countNonZero(img_grey)
    # print(z)
    if (z > z_thresh):
        warning_string = warning_p
    else:
        warning_string = warning_n

    return warning_string


# -------------------------- xxx ------------------------------------------------------

# MAIN PROGRAM ************************************************************************

# arguments are, filename, file type, packfolderPath
# filename_pdf=r'G1.pdf', utility_type="Gas", Root_directory_name='.'
def inputfunction(filename_pdf, utility_type, packFolderPath):
    # 1) Read a pdf file and take input its utility type
    # 2) Convert pdf into jpg and select the map area
    filename = os.path.join(packFolderPath, filename_pdf)
    #filename = Root_directory_name + '/' + filename_pdf
    print(filename)
    p = pdfbox.PDFBox()
    p.pdf_to_images(filename)
    file_name = filename[:-4]

    # the map image will be in E11.jpg which is the input for the next step
    utility_map_image_name = file_name + '1.jpg'

    # 3) Detect Sky Blue line in G maps
    img = cv2.imread(utility_map_image_name)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    warning_str_total = ''

    if (utility_type == 'Gas'):
        warning_str_total = ''

        # check for MP Mains Gas lines, return warning
        warning_str = threshold_filter(img, hsv_img, z_thresh_MP, low_GAS_MP, high_GAS_MP, warning_p_GAS_MP,
                                       warning_n_GAS_MP)
        warning_str_total = warning_str_total + warning_str

        # check for IP Mains Gas lines, return warning
        warning_str = threshold_filter(img, hsv_img, z_thresh_IP, low_GAS_IP, high_GAS_IP, warning_p_GAS_IP,
                                       warning_n_GAS_IP)
        warning_str_total = warning_str_total + warning_str

        # check for LHP Mains Gas lines, return warning
        warning_str = threshold_filter(img, hsv_img, z_thresh_LHP, low_GAS_LHP, high_GAS_LHP, warning_p_GAS_LHP,
                                       warning_n_GAS_LHP)
        warning_str_total = warning_str_total + warning_str

        if (warning_str_total == ''):
            warning_str_total = "NO MP-IP-LHP lines detected"

    if (utility_type == 'Electricity'):
        warning_str_total = ''
        # check for HV Electricity lines
        warning_str = threshold_filter(img, hsv_img, z_thresh_HV, low_ELEC_HV, high_ELEC_HV, warning_p_ELEC_HV,
                                       warning_n_ELEC_HV)
        warning_str_total = warning_str_total + warning_str

    # removing the creating image files
    # os.remove(utility_map_image_name)

    # ASving the output as JSON

    # warning_dict = {utility_type: warning_str_total}
    # return warning_dict

    return warning_str_total


    # print(json.dumps(warning_dict))
    # out_file = open(Root_directory_name + "/" + "ai_detection.json", "w")
    # json.dump(warning_dict, out_file, indent=6)
    # out_file.close()
    # return warning_str_total


# print(warning_str_total)
# if __name__ == '__main__':
#     inputfunction(filename_pdf=args["filename_pdf"], utility_type=args["utility_type"],
#                   Root_directory_name=args["rootdir"])
    # warning_str = inputfunction()
