import cv2
import numpy as np

# En mega guete comment schriebe
def alignment(raw_data):
    #Getting the centers of the sun images
    centers = []
    for im in raw_data:
        circles = cv2.HoughCircles(im,cv2.HOUGH_GRADIENT,dp=1,minDist=800,param1 = 10,param2=30,minRadius=470,maxRadius=480)
        circles = np.uint16(np.around(circles))
        middle = np.array([circles[0,0,0],circles[0,0,1]])
        centers.append(middle)

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
    return shifted_images
    
