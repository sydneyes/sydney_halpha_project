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

input_folder = "/Raw_images"

raw_data = []
image_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
for filename in image_files:
    # Check if the file has a supported image extension
    if filename.lower().endswith( '.tiff'):
        input_image_path = os.path.join(input_folder, filename)
        image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        raw_data.append(image)





cam_id = b"QHY5III200M-c8764d41ba464ec75"
path = os.path.join(os.path.dirname(__file__), 'qhyccd.dll')
cam_control = CameraControl(cam_id=cam_id, dll_path=path)

#success = cam_control.cam.so.InitQHYCCDResource()
n = 10
exposure_time = np.linspace(50, 220, n)
gain = 20
offset = 6


t1 = time.time()
images = []
for i in range(n):
    image = cam_control.single_frame(exposure_time[i], gain, offset)
    print(f"Image len:{image.shape}")
    print(image)
    images.append(image)
cam_control.close()
print(time.time()-t1)



#Processing the images
#First shifting the image
shifted_images = alignment(raw_data)

# Secondly doing post processing and labelling the image
text_image = image_processing(shifted_images)
output_path = 'sun.PNG'
cv2.imwrite(output_path, text_image)
print("Hi")
#Loading the images to the website
run_smbclient()







