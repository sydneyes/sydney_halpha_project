import os
import numpy as np
import time
from ctypes import *
import cv2
import time

from CameraControl import CameraControl
from alignment import alignment
from image_processing import image_processing
from upload_image import run_smbclient

cam_id = b"QHY5III200M-c8764d41ba464ec75"
path = os.path.join(os.path.dirname(__file__), 'qhyccd.dll')
cam_control = CameraControl(cam_id=cam_id, dll_path=path)

#success = cam_control.cam.so.InitQHYCCDResource()
n = 10
exposure_time = np.linspace(50, 220, n)
gain = 20
offset = 6

images = []
for i in range(n):
    image = cam_control.single_frame(exposure_time[i], gain, offset)
    print(image)
    images.append(image)
cam_control.close()

#Processing the images
#First shifting the image
shifted_images = alignment(images)

# Secondly doing post processing and labelling the image
text_image = image_processing(shifted_images)
output_path = '/home/ubuntu/docs/halpha/Sun_catching/sun.PNG'
cv2.imwrite(output_path, text_image)
print("Hi")
#Loading the images to the website
run_smbclient()
