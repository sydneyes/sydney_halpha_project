import os
import cv2
from CameraControl import CameraControl
import time


cam_id = b"QHY5III200M-c8764d41ba464ec75"
path = os.path.join(os.path.dirname(__file__), 'qhyccd.dll')
cam_control = CameraControl(cam_id=cam_id, dll_path=path)

#success = cam_control.cam.so.InitQHYCCDResource()

exposure_time = 400
gain = 20
offset = 6

for i in range(1000):
    image = cam_control.single_frame(exposure_time, gain, offset)
    print(f"Image len:{image.shape}")
    print(image)
    output_path = '/home/pi/docs/halpha/sun_catching/test_focus.tiff'
    cv2.imwrite(output_path, image)
    time.sleep(10)
cam_control.close()