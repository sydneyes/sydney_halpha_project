import os
import numpy as np
from ctypes import *
import time 


from qcam.image2ascii import np_array_to_ascii
from qcam.qCam import Qcam

class CameraControl:
    def __init__(self, cam_id, dll_path):
        self.cam_id = cam_id
        self.cam = Qcam(dll_path)
        self.success = self.cam.so.InitQHYCCDResource()
        print(self.success)
        self.opencamera = self.cam.so.OpenQHYCCD(self.cam_id)
        self.init_camera_param(self.cam_id)
        self.cam.camera_params[self.cam_id]['handle'] = self.opencamera
        success = self.cam.so.SetQHYCCDReadMode(self.cam.camera_params[self.cam_id]['handle'], c_uint32(0))
        self.cam.camera_params[self.cam_id]['stream_mode'] = c_uint8(0)
        success = self.cam.so.SetQHYCCDStreamMode(self.cam.camera_params[self.cam_id]['handle'], self.cam.camera_params[self.cam_id]['stream_mode'])
        success = self.cam.so.InitQHYCCD(self.cam.camera_params[self.cam_id]['handle'])

    

    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass
        #self.cam.so.CloseQHYCCD(self.cam.camera_params[self.cam_id]['handle'])
        

    def init_camera_param(self, cam_id):
        if cam_id not in self.cam.camera_params:
            self.cam.camera_params[cam_id] = {
                'connect_to_pc': False,
                'connect_to_sdk': False,
                'EXPOSURE': c_double(1000.0 * 1000.0),
                'GAIN': c_double(54.0),
                'OFFSET': c_double(4.5),
                'CONTROL_BRIGHTNESS': c_int(0),
                'CONTROL_GAIN': c_int(6),
                'CONTROL_OFFSET': c_int(10),
                'CONTROL_EXPOSURE': c_int(8),
                'CONTROL_CURTEMP': c_int(14),
                'CONTROL_CURPWM': c_int(15),
                'CONTROL_MANULPWM': c_int(16),
                'CONTROL_COOLER': c_int(18),
                'chip_width': c_double(),
                'chip_height': c_double(),
                'image_width': c_uint32(),
                'image_height': c_uint32(),
                'pixel_width': c_double(),
                'pixel_height': c_double(),
                'bits_per_pixel': c_uint32(),
                'mem_len': c_ulong(),
                'stream_mode': c_uint8(0),
                'channels': c_uint32(),
                'read_mode_number': c_uint32(),
                'read_mode_index': c_uint32(),
                'read_mode_name': c_char('-'.encode('utf-8')),
                'prev_img_data': c_void_p(0),
                'prev_img': None,
                'handle': None,
                'min_offset': c_double(),
                'max_offset': c_double(),
                'model': c_char(),
            }

    def close(self):
        self.cam.camera_params[self.cam_id]['prev_img'] = []
        self.cam.so.CloseQHYCCD(self.cam.camera_params[self.cam_id]['handle'])


    def scale_array(self, arr):
        min_val = np.min(arr)
        max_val = np.max(arr)
        print(min_val, max_val)
        scaled_array = ((arr - min_val) / (max_val - min_val)) * max_val
        return np.round(scaled_array).astype(np.uint16)
    


    def single_frame(self, exp_time, gain, offset):
        #print(self.cam.camera_params[self.cam_id]['prev_img'])
        t1 = time.time()
        
        success = self.cam.so.SetQHYCCDParam(self.cam.camera_params[self.cam_id]['handle'], self.cam.CONTROL_EXPOSURE, c_double(exp_time))
        success = self.cam.so.SetQHYCCDParam(self.cam.camera_params[self.cam_id]['handle'], self.cam.CONTROL_GAIN, c_double(gain))
        success = self.cam.so.SetQHYCCDBitsMode(self.cam.camera_params[self.cam_id]['handle'], self.cam.bit_depth_16)
        #print(success)
        #print(f"Init stuff: {time.time()-t1}")
        #t1 = time.time()
        os.makedirs(self.cam_id.decode('utf-8'), exist_ok=True)
        success = self.cam.so.GetQHYCCDChipInfo(self.cam.camera_params[self.cam_id]['handle'],
                                                byref(self.cam.camera_params[self.cam_id]['chip_width']),
                                                byref(self.cam.camera_params[self.cam_id]['chip_height']),
                                                byref(self.cam.camera_params[self.cam_id]['image_width']),
                                                byref(self.cam.camera_params[self.cam_id]['image_height']),
                                                byref(self.cam.camera_params[self.cam_id]['pixel_width']),
                                                byref(self.cam.camera_params[self.cam_id]['pixel_height']),
                                                byref(self.cam.camera_params[self.cam_id]['bits_per_pixel']))
        
        #print(f"get chip info: {time.time()-t1}")
        #t1 = time.time()
        self.cam.camera_params[self.cam_id]['mem_len'] = self.cam.so.GetQHYCCDMemLength(self.cam.camera_params[self.cam_id]['handle'])
        #print(self.cam.camera_params[self.cam_id])
        
        #print(f"Memory length in params dics:{self.cam.camera_params[self.cam_id]['mem_len']}")
        #if self.cam.camera_params[self.cam_id]["mem_len"] >= 2**32 -1:
        #    return None
        tmp = (c_uint16 * int((self.cam.camera_params[self.cam_id]['mem_len']) / 2))()
        #print(tmp)
        self.cam.camera_params[self.cam_id]['prev_img_data'] = tmp
        
        i_w = self.cam.camera_params[self.cam_id]['image_width'].value
        i_h = self.cam.camera_params[self.cam_id]['image_height'].value

        self.cam.so.SetQHYCCDResolution(self.cam.camera_params[self.cam_id]['handle'], c_uint32(0), c_uint32(0), c_uint32(i_w), c_uint32(i_h))
        #print(f"Set resolution: {time.time()-t1}")
        #t1 = time.time()
        success = self.cam.so.ExpQHYCCDSingleFrame(self.cam.camera_params[self.cam_id]['handle'])
        success = self.cam.so.SetQHYCCDParam(self.cam.camera_params[self.cam_id]['handle'], self.cam.CONTROL_OFFSET, c_double(offset))

        image_width_byref = c_uint32()
        image_height_byref = c_uint32()
        bits_per_pixel_byref = c_uint32()

        success = self.cam.so.GetQHYCCDSingleFrame(self.cam.camera_params[self.cam_id]['handle'], 
                                                   byref(image_width_byref), 
                                                   byref(image_height_byref), 
                                                   byref(bits_per_pixel_byref), 
                                                   byref(self.cam.camera_params[self.cam_id]['channels']), 
                                                   byref(self.cam.camera_params[self.cam_id]['prev_img_data']))
        #print(f"GetQHYCCDSingleFrame: {time.time()-t1}")
        #t1 = time.time()
        self.cam.camera_params[self.cam_id]['prev_img'] = np.ctypeslib.as_array(self.cam.camera_params[self.cam_id]['prev_img_data'])
        image_size = i_w * i_h
        self.cam.camera_params[self.cam_id]['prev_img'] = self.cam.camera_params[self.cam_id]['prev_img'][0:image_size]
        image = np.reshape(self.cam.camera_params[self.cam_id]['prev_img'], (i_h, i_w))
        #print(f"image to numpy: {time.time()-t1}")
        return image
        # print(image)

        # pil_image = PIL_image.fromarray(image)
        # name = 'test'
        # pil_image.save(f'/home/pi/Schreibtisch/Webcam1/Processing/Raw_PNG/{name}_{count}.tiff')

        # self.cam.camera_params[cam_id]['prev_img'] = []
        # self.cam.so.CloseQHYCCD(self.cam.camera_params[cam_id]['handle'])

def main():
    print("Let's take a test picture")
    cam_id = b"QHY5III200M-c8764d41ba464ec75"
    path = os.path.join(os.path.dirname(__file__), 'qhyccd.dll')
    cam_control = CameraControl(cam_id=cam_id, 
                                dll_path=path)
    
    #success = cam_control.cam.so.InitQHYCCDResource()
    exposure_time = 15
    gain = 10
    offset = 140
    image = cam_control.single_frame(exposure_time, gain, offset)
    print(f"image len:{len(image)}")
    cam_control.close()



# Usage example
if __name__ == "__main__":
    main()

    """
    dll_path = os.path.join(os.path.dirname(__file__), 'qhyccd.dll')
    cam_id = b"QHY5III200M-c8764d41ba464ec75"
    camera_controller = CameraController(dll_path)

    # You can now use camera_controller to perform camera operations, for example:
    # camera_controller.single_frame(cam_id, exp_time, gain, offset, count, folder_name)
    qcam_capture = CameraController(dll_path)
    exp_time = 15000.0  # Exposure time in microseconds
    gain = 10.0         # Gain
    offset = 10.0       # Offset
    count = 1           # Image count or identifier
    folder_name = "test_images"  # Folder to save the images

    # Capturing a single frame
    # Note: Ensure the folder exists or is created within the `single_frame` method
    qcam_capture.single_frame(cam_id, exp_time, gain, offset, count, folder_name)

    print("Image capture completed.")
    """