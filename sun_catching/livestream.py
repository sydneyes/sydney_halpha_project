import os
import numpy as np
import time
from ctypes import *
import cv2
import time
import sys

from CameraControl import CameraControl
from alignment import alignment
from image_processing import image_processing
from upload_image import run_smbclient

cam_id = b"QHY5III200M-c8764d41ba464ec75"
path = os.path.join(os.path.dirname(__file__), 'qhyccd.dll')
cam_control = CameraControl(cam_id=cam_id, dll_path=path)
#success = cam_control.cam.so.InitQHYCCDResource()
n = 10
exposure_time = np.linspace(400, 2000, n)
gain = 20
offset = 6

with open("error.txt","w") as file:
    file.write("")
while True:
    images = []
    for i in range(n):
        try:
            image = cam_control.single_frame(exposure_time[i], gain, offset)
            print(images)
            images.append(image)
        except Exception as e:
            cam_control.close()
            print(f"An error occured with the camera: {e}")
            print("Please go to the script that manages the camera:")
            print("/home/pi/docs/halpha/sun_catching/CameraControl.py")
            with open("error.txt", "a") as file:
                file.write("camera_error")
            sys.exit("Problems while handling the camera")
        
    if len(images) == n:
        #Processing the images
        #First shifting the image
        shifted_images = alignment(images)
        if shifted_images != None:
            # Secondly doing post processing and labelling the image
            text_image = image_processing(shifted_images)
            output_path = '/home/ubuntu/docs/halpha/sun_catching/sun.PNG'
            cv2.imwrite(output_path, text_image)
            #Loading the images to the websites
            run_smbclient()
