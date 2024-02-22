import os
import numpy as np
import time
from PIL import Image as PIL_image
from astropy.io import fits
from datetime import datetime
import json
from qcam.image2ascii import np_array_to_ascii
from qcam.qCam import *

cam = Qcam(os.path.join(os.path.dirname(__file__), 'qhyccd.dll'))




def init_camera_param(cam_id):
    if not cam.camera_params.keys().__contains__(cam_id):
        cam.camera_params[cam_id] = {'connect_to_pc': False,
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


def scale_array(arr):
    # Find the minimum and maximum values in the array
    min_val = np.min(arr)
    max_val = np.max(arr)
    print(min_val)
    print(max_val)

    # Scale the array to the range [0, 65535]
    scaled_array = ((arr - min_val) / (max_val - min_val)) * max_val

    # Round to integers
    scaled_array = np.round(scaled_array).astype(np.uint16)
 

    return scaled_array



def single_frame(cam_id, exp_time, gain, offset, count):

    opencamera = cam.so.OpenQHYCCD(cam_id)		#Open the Camera with the ID: cam_id


    init_camera_param(cam_id)			        #Initialize the camera paramters
    cam.camera_params[cam_id]['handle'] = opencamera
    print(cam.camera_params)
    print(cam.camera_params[cam_id]['prev_img'])

    # Set Read mode and stream mode:

    #set read mode: 
    success = cam.so.SetQHYCCDReadMode(cam.camera_params[cam_id]['handle'], c_uint32(0))


    #set stream mode first: I think (0 = Stream_single_mode) , (1 = stream_live_mode) possible

    cam.camera_params[cam_id]['stream_mode'] = c_uint8(0)
    success = cam.so.SetQHYCCDStreamMode(cam.camera_params[cam_id]['handle'], cam.camera_params[cam_id]['stream_mode'])


    #Initialize the Camera:

    success = cam.so.InitQHYCCD(cam.camera_params[cam_id]['handle'])

    #change the exposure time to 15ms
    success = cam.so.SetQHYCCDParam(cam.camera_params[cam_id]['handle'], cam.CONTROL_EXPOSURE, c_double(exp_time))
   

    success = cam.so.SetQHYCCDParam(cam.camera_params[cam_id]['handle'], cam.CONTROL_GAIN, c_double(gain))


    ##########
    #Set Bits_mode: (8bits or 16 bits possible)

    success = cam.so.SetQHYCCDBitsMode(cam.camera_params[cam_id]['handle'], cam.bit_depth_16)
    print(success) 

    ##########


    #Get the Chip_info of the camera on cam.camera_params:

    os.makedirs(cam_id.decode('utf-8'), exist_ok=True)
    success = cam.so.GetQHYCCDChipInfo(cam.camera_params[cam_id]['handle'],
                                       byref(cam.camera_params[cam_id]['chip_width']),
                                       byref(cam.camera_params[cam_id]['chip_height']),
                                       byref(cam.camera_params[cam_id]['image_width']),
                                       byref(cam.camera_params[cam_id]['image_height']),
                                       byref(cam.camera_params[cam_id]['pixel_width']),
                                       byref(cam.camera_params[cam_id]['pixel_height']),
                                       byref(cam.camera_params[cam_id]['bits_per_pixel']))


    cam.camera_params[cam_id]['mem_len'] = cam.so.GetQHYCCDMemLength(cam.camera_params[cam_id]['handle'])

    cam.camera_params[cam_id]['prev_img_data'] = (c_uint16 * int((cam.camera_params[cam_id]['mem_len'])/2))()     


    #SET RESOLUTION:

    i_w = cam.camera_params[cam_id]['image_width'].value 	#1920
    i_h = cam.camera_params[cam_id]['image_height'].value	#1080


    cam.so.SetQHYCCDResolution(cam.camera_params[cam_id]['handle'], c_uint32(0), c_uint32(0), c_uint32(i_w), c_uint32(i_h))

    ####################


    #We now take a single frame:

    success = cam.so.ExpQHYCCDSingleFrame(cam.camera_params[cam_id]['handle'])

    success = cam.so.SetQHYCCDParam(cam.camera_params[cam_id]['handle'], cam.CONTROL_OFFSET, c_double(offset))

    image_width_byref = c_uint32()
    image_height_byref = c_uint32()
    bits_per_pixel_byref = c_uint32() 



    success = cam.so.GetQHYCCDSingleFrame(cam.camera_params[cam_id]['handle'], byref(image_width_byref), byref(image_height_byref), byref(bits_per_pixel_byref), byref(cam.camera_params[cam_id]['channels']), byref(cam.camera_params[cam_id]['prev_img_data']))


    #####################

    #Save the image:

    cam.camera_params[cam_id]['prev_img'] = np.ctypeslib.as_array(cam.camera_params[cam_id]['prev_img_data'])
    image_size = i_w * i_h 
    image_size = image_size
    cam.camera_params[cam_id]['prev_img'] = cam.camera_params[cam_id]['prev_img'][0:image_size]

    image = np.reshape(cam.camera_params[cam_id]['prev_img'], (i_h, i_w))

    print(image)

    #image = scale_array(image)

    pil_image = PIL_image.fromarray(image)

    name = 'test'

    #converted_image = pil_image.convert('L')
    
    pil_image.save(r'/home/pi/Schreibtisch/Webcam1/Processing/Raw_PNG/%s_%s.tiff' % (name, count))
    #pil_image.save(r'/home/pi/Schreibtisch/Webcam1/QHY5III200M-c8764d41ba464ec75/%s_%s.tiff' % (name, count))

    #pil_image.show()

    #####################
    cam.camera_params[cam_id]['prev_img'] = []
    # close the camera in the end:
    cam.so.CloseQHYCCD(cam.camera_params[cam_id]['handle'])
 



#This is just to test the camera by taking a single frame


print("lets take a testpicture")

cam_id = b"QHY5III200M-c8764d41ba464ec75"
success = cam.so.InitQHYCCDResource()

exposure_time = 15
gain = 10
offset = np.linspace(0,255,5)

counter = 0


for i in range(3):
    single_frame(cam_id, exposure_time, gain, offset[i], counter+i)