import os
import numpy as np
from ctypes import *
import cv2
import time
import sys
import logging
import subprocess

from CameraControl import CameraControl
from alignment import alignment
from image_processing import image_processing
from upload_image import run_smbclient

cam_id = b"QHY5III200M-c8764d41ba464ec75"
path = os.path.join(os.path.dirname(__file__), 'qhyccd.dll')
cam_control = CameraControl(cam_id=cam_id, dll_path=path)
#success = cam_control.cam.so.InitQHYCCDResource()
n = 10
exposure_time = np.linspace(500, 2000, n)
gain = 20
offset = 6

log_file_path = '/home/pi/docs/halpha/sun_catching/error_log.txt'
logging.basicConfig(filename=log_file_path, level=logging.ERROR)
with open(log_file_path, 'w'):
    pass

while True:
    try:
        images = []
        for i in range(n):
            image = cam_control.single_frame(exposure_time[i], gain, offset)
            print(image)
            normalized_data = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
            image = np.uint8(normalized_data)
            output_path = f'/home/pi/docs/halpha/sun_catching/test_files/sun_halpha_{i}.tiff'
            cv2.imwrite(output_path,image)
            images.append(image)
        if len(images) == n:
            #Processing the images
            #First shifting the image
            shifted_images = alignment(images, log_file_path)
            if shifted_images != None:
                # Secondly doing post processing and labelling the image
                text_image = image_processing(shifted_images)
                output_path = '/home/pi/docs/halpha/sun_catching/sun.PNG'
                cv2.imwrite(output_path, text_image)
                #Loading the images to the websites

                run_smbclient()
    except TypeError:
        with open(log_file_path, 'w'):
            pass
        with open(log_file_path, 'w')as file:
            file.write("Circle detection not successfull. Retrying....")
        pass
    except subprocess.CalledProcessError:
        with open(log_file_path, 'w'):
            pass
        with open(log_file_path, 'w')as file:
            file.write("Uploading image not successfull. Retrying....")
        pass
    except Exception as e:
        print(e)
        with open(log_file_path, 'w'):
                    pass
        logging.error(f"{str(e)}", exc_info=True)
        sys.exit(f"An error occurred: {str(e)}")    
