import cv2
import numpy as np
import os

input_folder = "/home/pi/docs/halpha/sun_catching/Raw_images"
raw_data = []
image_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
for filename in image_files:
    # Check if the file has a supported image extension
    if filename.lower().endswith( '.tiff'):
        input_image_path = os.path.join(input_folder, filename)
        image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        raw_data.append(image)
print(raw_data)

#Getting the centers of the sun images
centers = []
for im in raw_data:
    print("Hi")
    circles = cv2.HoughCircles(im,cv2.HOUGH_GRADIENT,dp=1,minDist=800,param1 = 10,param2=30,minRadius=470,maxRadius=480)
    print("Hi")
    circles = np.uint16(np.around(circles))
    middle = np.array([circles[0,0,0],circles[0,0,1]])
    centers.append(middle)
print(centers)
'''
#Calculating the values for the shift
coordinates = np.empty((0,2))
coordinates = np.vstack((coordinates, centers))
for i in range(len(coordinates[:])-1):
    coordinates[i+1] = coordinates[i+1] - coordinates[0]
coordinates[0] = np.zeros(2)
shifts =  -1*coordinates

#Shifting the images
shifted_images = []
for i, image in enumerate(raw_data):
    shift_x, shift_y = shifts[i]
    rows, cols = image.shape[:2]
    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    shifted_image = cv2.warpAffine(image, M, (cols, rows))
    normalized_data = cv2.normalize(shifted_image, None, 0, 255, cv2.NORM_MINMAX)
    shifted_image = np.uint8(normalized_data)
    shifted_images.append(shifted_image)
'''
    