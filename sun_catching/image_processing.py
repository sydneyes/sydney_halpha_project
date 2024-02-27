import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import math
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime



def points_on_circle(center_x, center_y, radius, num_points):
    points = []
    angle_step = 360 / num_points

    for i in range(num_points):
        angle = math.radians(i * angle_step)
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))
        points.append((x, y))

    return points

def sum_values_on_circle(image, center_x, center_y, radius, num_points):
    points = points_on_circle(center_x, center_y, radius, num_points)
    total_sum = 0

    for point in points:
        x, y = point
        if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
            pixel_value = image[y, x]
            total_sum += pixel_value

    return total_sum

def plot_values_for_radii(image, center_x, center_y, min_radius, max_radius, num_points):
    radii = list(range(min_radius, max_radius + 1))
    sums = []
    for radius in radii:
        result = sum_values_on_circle(image, center_x, center_y, radius, num_points)
        sums.append(result)
    min_rad = radii[np.argmin(sums)]
    return min_rad


def set_values_outside_radius_to_zero(image, center_x, center_y, min_radius):
    y_indices, x_indices = np.indices(image.shape)
    distances = np.sqrt((x_indices - center_x)**2 + (y_indices - center_y)**2)
    image[distances > min_radius] = 0
    return image

#Doing intensity stretching to the image with the histogramm
def stretch_intensity(image, min_intensity, max_intensity, new_min, new_max):
    # Flatten the 2D array to 1D
    flattened_image = image.flatten()

    # Calculate the histogram
    hist, bins = np.histogram(flattened_image, bins=256, range=[0, 256])

    # Find the indices corresponding to the range in the histogram
    lower_index = np.argmax(bins >= min_intensity)
    upper_index = np.argmax(bins >= max_intensity)

    # Get the limits for the specified range
    lower_limit = bins[lower_index]
    upper_limit = bins[upper_index]

    # Create a mask to identify the values within the specified range
    mask = (flattened_image >= lower_limit) & (flattened_image <= upper_limit)

    # Stretch only the specified range in the flattened image using the mask
    stretched_image = flattened_image.copy()
    stretched_image[mask] = ((stretched_image[mask] - lower_limit) * (new_max - new_min)) / (upper_limit - lower_limit) + new_min

    # Reshape back to 2D
    stretched_image = stretched_image.reshape(image.shape)

    return stretched_image

#Adding text to the image
def write_text(image, text, text_position, font_scale):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_thickness = 2
    color = (255, 255, 255)  # Weiß

    text_image = cv2.putText(image, text, text_position, font, font_scale, color, font_thickness, cv2.LINE_AA)
    return text_image



def image_processing(images):        
    #Blurring the image with a Gaussian filter to get the shadows made by the telescope. 
    # Dividing the raw image with the shadow pattern to get a evenly illuminated disk and stretching the image over the fulll dynamic range 
    gaus_images = []
    kernel_size = 256
    sigma = 64
    gaussian_kernel = cv2.getGaussianKernel(kernel_size, sigma)
    gaussian_kernel_2d = np.outer(gaussian_kernel, gaussian_kernel)
    for img in images:
        gaus = cv2.filter2D(img, cv2.CV_8U, kernel=gaussian_kernel_2d)
        raw_image = np.divide(img, gaus)
    
        normalized_data = cv2.normalize(raw_image, None, 0, 255, cv2.NORM_MINMAX)
        raw_image = np.uint8(normalized_data)
        
        hist, bins = np.histogram(raw_image, bins=50, density=True)
        cdf = np.cumsum(hist * np.diff(bins))
    
        lower_threshold = 0.01  # 5% on the lower end
        upper_threshold = 0.999  # 95% on the upper end
        lower_index = np.argmax(cdf >= lower_threshold)
        upper_index = np.argmax(cdf >= upper_threshold)
    
        lower_limit = bins[lower_index]
        upper_limit = bins[upper_index]
    
        max_value = upper_limit
        min_value = lower_limit
        new_min = 0
        new_max = 256
        sharpened = np.clip(raw_image, min_value, max_value)
    
        stretched_image = ((sharpened - min_value)*(new_max- new_min)) / (max_value-min_value) + new_min
        gaus_images.append(stretched_image)
        
    
    # Stacking the gaus images
    compensator = cv2.createMergeMertens()
    data_image = compensator.process(gaus_images)
    normalized_data = cv2.normalize(data_image, None, 0, 255, cv2.NORM_MINMAX)
    raw_gaus_image = np.uint8(normalized_data)
    
    # Stacking the raw images
    compensator = cv2.createMergeMertens()
    data_image = compensator.process(images)
    normalized_data = cv2.normalize(data_image, None, 0, 255, cv2.NORM_MINMAX)
    raw_image = np.uint8(normalized_data)
    
    
    
    # Getting the average of the to stacked images (raw and with shadow correction)
    mean = np.mean([raw_gaus_image, raw_image], axis=0)
    normalized_data = cv2.normalize(mean, None, 0, 255, cv2.NORM_MINMAX)
    mean = np.uint8(normalized_data)
    
    # Getting the center of the circle
    circles = cv2.HoughCircles(mean,cv2.HOUGH_GRADIENT,dp=1,minDist=800,param1 = 10,param2=30,minRadius=470,maxRadius=480)
    circles = np.uint16(np.around(circles))
    middle = np.array([circles[0,0,0],circles[0,0,1]])
    
    # Setting everything outside the sun to 0 
    num_points = 1000
    min_radius = plot_values_for_radii(mean, middle[0], middle[1], 400, 600, num_points) + 20
    image = set_values_outside_radius_to_zero(mean,middle[0],middle[1], min_radius) 
    normalized_data = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    image = np.uint8(normalized_data)
    
    # Stretching the image so the edge of the sun and the structure is better visible
    
    # Calculating the start and end of the peaks
    flattened_image = image.flatten()
    hist, bins = np.histogram(flattened_image, bins=256, range=[0, 256])
    cdf = np.cumsum(hist * np.diff(bins))
    
    threshold_y = 500 
    
    varying_cdf_intervals = []
    current_interval_start = bins[0]
    
    for i in range(1, len(bins) - 1):
        cdf_variation = abs(cdf[i] - cdf[i - 1])
        if cdf_variation >= threshold_y:
            current_interval_end = bins[i - 1]
            varying_cdf_intervals.append((current_interval_start, current_interval_end))
            current_interval_start = bins[i]
    
    
    intervals = []
    varying_cdf_intervals.append((current_interval_start, bins[-1]))
    for interval in varying_cdf_intervals:
        start, end = interval
        if end - start > 5:
            intervals.append(interval)
    
    
    #Stretching the peaks 
    # Set the range you want to stretch
    min_intensity_low = intervals[0][1]
    max_intensity_high = intervals[1][0]
    
    # Define the new min and max values for stretching
    new_min = 0
    new_max = 255/2
    
    # Stretch the specified range in the image
    stretched_image = stretch_intensity(image, min_intensity_low, max_intensity_high, new_min, new_max)
    
    # Set the range you want to stretch
    min_intensity = intervals[1][1]
    max_intensity = intervals[2][0]
    
    # Define the new min and max values for stretching
    new_min = 100
    new_max = 255
    
    # Stretch the specified range in the image
    stretched_image = stretch_intensity(stretched_image, min_intensity, max_intensity, new_min, new_max)
    normalized_data = cv2.normalize(stretched_image, None, 0, 255, cv2.NORM_MINMAX)
    stretched_image = np.uint8(normalized_data)
    
    # Shifting the sun to the center of the image
    image = stretched_image

    image_height, image_width = image.shape[:2]

    shift_x = image_width // 2 - middle[0]
    shift_y = image_height // 2 - middle[1]
    
    translation_matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    shifted_image = cv2.warpAffine(image, translation_matrix, (image_width, image_height))

    # Coloring the image in H-Alpha
    cmap = LinearSegmentedColormap.from_list('halpha_cmap', ['black', 'red'], N=256)
    halpha_colored = cmap(shifted_image)
    normalized_data = cv2.normalize(halpha_colored, None, 0, 255, cv2.NORM_MINMAX)
    halpha_colored = np.uint8(normalized_data)

    halpha_colored_bgr = cv2.cvtColor(halpha_colored, cv2.COLOR_RGB2BGR)


    # Writing the date, location and poles on to the image
    text_position = (50, 50)
    text = 'PMOD/WRC Davos'
    text_image = write_text(halpha_colored_bgr, text, text_position, 1)
    
    text_position = (1300, 50)
    current_utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    text = 'Halpha ' + current_utc_time
    text_image = write_text(text_image, text, text_position,1)
    
    rad = min_radius
    
    text_position = (int(image_width/2), int(image_height/2-rad))
    text = 'N'
    text_image = write_text(text_image, text, text_position, 0.5)
    
    
    text_position = (int(image_width/2 + rad), int(image_height/2))
    text = 'E'
    text_image = write_text(text_image, text, text_position, 0.5)
    
    
    text_position = (int(image_width/2), int(image_height/2 + rad))
    text = 'S'
    text_image = write_text(text_image, text, text_position, 0.5)
    
    
    text_position = (int(image_width/2 - rad -20), int(image_height/2))
    text = 'W'
    text_image = write_text(text_image, text, text_position, 0.5)
    
    normalized_data = cv2.normalize(text_image, None, 0, 255, cv2.NORM_MINMAX)
    text_image = np.uint8(normalized_data)

    return text_image   