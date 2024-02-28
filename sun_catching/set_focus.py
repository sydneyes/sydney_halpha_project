import os
import cv2
from CameraControl import CameraControl


cam_id = b"QHY5III200M-c8764d41ba464ec75"
path = os.path.join(os.path.dirname(__file__), 'qhyccd.dll')
cam_control = CameraControl(cam_id=cam_id, dll_path=path)

#success = cam_control.cam.so.InitQHYCCDResource()
n = 10
exposure_time = 1000
gain = 20
offset = 6

while True:
    image = cam_control.single_frame(exposure_time, gain, offset)
    print(f"Image len:{image.shape}")
    print(image)
    cam_control.close()
    output_path = '/home/ubuntu/docs/halpha/Sun_catching/test_focus.PNG'
    cv2.imwrite(output_path, image)
