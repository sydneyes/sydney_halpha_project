import cv2
import numpy as np

def find_circle_midpoint(image_path):
    # Load the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use Canny edge detection to find edges
    edges = cv2.Canny(blurred, 50, 150)
    print(edges)
    # Find contours
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(contours)
    # Find the contour with the largest area
    contour = max(contours, key=cv2.contourArea)

    # Get the centroid of the contour
    M = cv2.moments(contour)
    if M["m00"] != 0:
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
        return center_x, center_y
    else:
        print("No contour detected in the image.")
        return None
    
image_path = "test_files/sun_halpha_0.tiff"
circle_midpoint = find_circle_midpoint(image_path)
print(circle_midpoint)


