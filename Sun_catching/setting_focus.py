import os
import numpy as np
import time
from ctypes import *
import cv2
import time

from test import CameraControl


cam_id = b"QHY5III200M-c8764d41ba464ec75"
path = os.path.join(os.path.dirname(__file__), 'qhyccd.dll')
cam_control = CameraControl(cam_id=cam_id, dll_path=path)

n = 10
exposure_time = 1000
gain = 20
offset = 6

for i in range(1000):
    image = cam_control.single_frame(exposure_time, gain, offset)
    output_path = r'/home/pi/Schreibtisch/Sun_catching/setting_focus/focus.tiff'
    cv2.imwrite(output_path, image)
    print(i)
cam_control.close()