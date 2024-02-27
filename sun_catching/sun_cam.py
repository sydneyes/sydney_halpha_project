import os
import numpy as np
from qcam.image2ascii import np_array_to_ascii
from qcam.qCam import Qcam, c_double, c_int, c_uint32, c_char, c_void_p, c_ulong, c_uint8, byref, c_uint16
import logging

logging.basicConfig(level=logging.INFO,  # Set to DEBUG for more detailed logs
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
                    #filename='sun_cam.log',  # Log to a file, remove this to log to stdout
                    #filemode='a')


class Sun_cam():
    def __init__(self, cam_id):
        self.logger = logging.getLogger('Sun_cam')
        self.cam_id = cam_id
        self.logger.info(f'Initializing camera with ID: {cam_id}')
        self.ddl_path = os.path.join(os.path.dirname(__file__), 'qhyccd.dll')
        self.logger.info(f'Set ddl path for Qcam to : {self.ddl_path}')

        self.cam = Qcam(self.ddl_path)
        self.opencamera = self.cam.so.OpenQHYCCD(cam_id)
        self.init_camera_param()
        self.cam.camera_params[cam_id]['handle'] = self.opencamera
        self.init_camera_mode()
    

    def __enter__(self):
        self.opencamera = self.cam.so.OpenQHYCCD(self.cam_id)
        return self
    

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.cam.so.CloseQHYCCD(self.cam.camera_params[self.cam_id]['handle'])
    

    def init_camera_param(self):
        if not self.cam.camera_params.keys().__contains__(self.cam_id):
            self.cam.camera_params[self.cam_id] = {'connect_to_pc': False,
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
            

    def set_read_mode(self):
        try:
            self.success = self.cam.so.SetQHYCCDReadMode(self.cam.camera_params[self.cam_id]['handle'], c_uint32(0))
            self.logger.info(f'CMD set_read_mode success response: {self.success}')
        except Exception as exp:
            self.logger.error(f'Error CMD set_read_mode response: {exp}')


    def set_stream_mode(self):
        try:
            self.cam.camera_params[self.cam_id]['stream_mode'] = c_uint8(0)
            self.success = self.cam.so.SetQHYCCDStreamMode(self.cam.camera_params[self.cam_id]['handle'], 
                                                        self.cam.camera_params[self.cam_id]['stream_mode'])
            self.logger.info(f'CMD set_stream_mode success response: {self.success}')

        except Exception as exp:
            self.logger.error(f'Error CMD set_stream_mode response: {exp}')
    

    def set_param(self, param, param_val):
        try:
            self.logger.info(f'CMD set_param parameter: {param}, param_value: {param_val}')
            self.success = self.cam.so.SetQHYCCDParam(self.cam.camera_params[self.cam_id]['handle'], 
                                                        param, 
                                                        param_val)
            self.logger.info(f'CMD set_param success response: {self.success}')
        except Exception as exp:
            self.logger.error(f'Error CMD set_stream_mode response: {exp}')
         

    def set_exposure(self, exposure_time=15):
        self.exposure_time = exposure_time
        self.set_param(self.cam.CONTROL_EXPOSURE, 
                       c_double(self.exposure_time))
    

    def set_gain(self, gain=10):
        self.gain = gain
        self.set_param(self. cam.CONTROL_GAIN,
                        c_double(self.gain))
    

    def set_bit_depth(self, bit_depth=16):
        if int(bit_depth) == 8 | bit_depth == self.cam.bit_depth_8:
            self.bit_depth = self.cam.bit_depth_8
        elif int(bit_depth) == 16  | bit_depth == self.cam.bit_depth_16:
            self.bit_depth = self.cam.bit_depth_16
        else:
            raise ValueError("Value of bit_depth is not in valid values [8, 16, cam.bit_depth_8, cam.bit_depth_16]")

        try:
            self.success = self.cam.so.SetQHYCCDBitsMode(self.cam.camera_params[self.cam_id]['handle'], 
                                                         self.bit_depth)
            self.logger.info(f'CMD set_bit_depth success response: {self.success}')
        except Exception as exp:
            self.logger.error(f'Error CMD set_bit_depth response: {exp}')

    
    def get_chip_info(self):
        try:
            os.makedirs(self.cam_id.decode('utf-8'), exist_ok=True)
            self.success = self.cam.so.GetQHYCCDChipInfo(self.cam.camera_params[self.cam_id]['handle'],
                                                byref(self.cam.camera_params[self.cam_id]['chip_width']),
                                                byref(self.cam.camera_params[self.cam_id]['chip_height']),
                                                byref(self.cam.camera_params[self.cam_id]['image_width']),
                                                byref(self.cam.camera_params[self.cam_id]['image_height']),
                                                byref(self.cam.camera_params[self.cam_id]['pixel_width']),
                                                byref(self.cam.camera_params[self.cam_id]['pixel_height']),
                                                byref(self.cam.camera_params[self.cam_id]['bits_per_pixel']))
            
            self.logger.info(f'CMD get_chip_info success response: {self.success}')
        except Exception as exp:
            self.logger.error(f'Error CMD get_chip_info response: {exp}')

    def get_mem_length(self):
        try:
            self.mem_length = self.cam.so.GetQHYCCDMemLength(self.cam.camera_params[self.cam_id]['handle'])
            self.cam.camera_params[self.cam_id]['mem_len'] = self.mem_length
            self.logger.info(f'CMD get_mem_length success response: {self.mem_length}')
        except Exception as exp:
            self.logger.error(f'Error CMD get_mem_length response: {exp}')

    def set_camare_res(self):
        try:
            self.mem_length = self.cam.so.GetQHYCCDMemLength(self.cam.camera_params[self.cam_id]['handle'])
            self.cam.camera_params[self.cam_id]['mem_len'] = self.mem_length
            self.logger.info(f'CMD set_camare_res success response 1: {self.mem_length} \n\n')
        except Exception as exp:
            self.logger.error(f'Error CMD set_camare_res response 1: {exp} \n\n')

        try:       
            self.prev_img_data = (c_uint16 * int((self.cam.camera_params[self.cam_id]['mem_len'])/2))()
            self.logger.info(f'CMD set_camare_res success response 2: {self.prev_img_data}\n\n')
        except Exception as exp:
            self.logger.error(f'Error CMD set_camare_res response 2: {exp}\n\n')

        try:    
            self.cam.camera_params[self.cam_id]['prev_img_data'] = self.prev_img_data 
            self.i_w = self.cam.camera_params[self.cam_id]['image_width'].value 	#1920
            self.i_h = self.cam.camera_params[self.cam_id]['image_height'].value	#1080
            self.logger.info(f'CMD set_camare_res get width: {self.i_w}')
            self.logger.info(f'CMD set_camare_res get height: {self.i_h}\n\n')
        except Exception as exp:
            self.logger.error(f'Error CMD set_camare_res response: {exp}\n\n')    
        #SET RESOLUTION:

        
        try:
            self.cam.so.SetQHYCCDResolution(self.cam.camera_params[self.cam_id]['handle'], 
                                        c_uint32(0), 
                                        c_uint32(0), 
                                        c_uint32(self.i_w), 
                                        c_uint32(self.i_h))   
            self.logger.info(f'CMD set_camare_res Set Res success')
        except Exception as exp:
            self.logger.error(f'Error CMD set_camare_res response: {exp}\n\n')   
               

    def init_camera_mode(self):
        self.set_read_mode()
        self.set_stream_mode()
        self.set_exposure()
        self.set_gain()
        self.set_bit_depth()
        self.get_chip_info()
        self.get_mem_length()
        self.set_camare_res()
    

        


    def get_image(self, offset=10):
        self.offset = offset
        self.success = self.cam.so.ExpQHYCCDSingleFrame(self.cam.camera_params[self.cam_id]['handle'])

        self.success = self.cam.so.SetQHYCCDParam(self.cam.camera_params[self.cam_id]['handle'], 
                                                  self.cam.CONTROL_OFFSET, c_double(self.offset))

        image_width_byref = c_uint32()
        image_height_byref = c_uint32()
        bits_per_pixel_byref = c_uint32()
        self.success = self.cam.so.GetQHYCCDSingleFrame(self.cam.camera_params[self.cam_id]['handle'], 
                                                        byref(image_width_byref), 
                                                        byref(image_height_byref), 
                                                        byref(bits_per_pixel_byref), 
                                                        byref(self.cam.camera_params[self.cam_id]['channels']), 
                                                        byref(self.cam.camera_params[self.cam_id]['prev_img_data']))
        
        self.prev_img = np.ctypeslib.as_array(self.cam.camera_params[self.cam_id]['prev_img_data'])
        self.cam.camera_params[self.cam_id]['prev_img'] = self.prev_img
        image_size = self.i_w * self.i_h 
        self.image_size = image_size
        self.cam.camera_params[self.cam_id]['prev_img'] = self.cam.camera_params[self.cam_id]['prev_img'][0:self.image_size]

        image = np.reshape(self.cam.camera_params[self.cam_id]['prev_img'], (self.i_h, self.i_w))
        return image





if __name__ == "__main__":
    cam_id = b"QHY5III200M-c8764d41ba464ec75"
    cam = Sun_cam(cam_id)
    with cam as c:
        img = c.get_image()
        print(img)



