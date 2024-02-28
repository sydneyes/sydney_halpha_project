# Aligmnet
This Script is to shift the images so that the sun in the different images is aligned. We have to do the aligment of the images to get better results in the following image processing steps. 

Despite the fact that the telescope is located on a tracking device there are shifts of the sun in the different images

### Code Description
The function for the aligment is separated in 3 steps: 

- In the first part the centers of the sun images are located with the HoughCircles function from cv2.
```python
circles = cv2.HoughCircles(im,cv2.HOUGH_GRADIENT,dp=1,minDist=800,param1 = 10,param2=30,minRadius=470,maxRadius=480)
```
- In the second step the shift of the images is calculated based on the center of the first image.

- In the end the images are shifted with the function warpAffine from cv2.
```python
cv2.warpAffine(image, M, (cols, rows))
```

### Usage 
This function for the aligment is mainly used in a script where we take images with different exposure times and merge them later together to make a livestream. This can be found [here](https://github.com/pmodwrc/halpha/blob/main/sun_catching/process.py).

## Reference

### Sources
The function was build with [OpenCV](https://docs.opencv.org/4.x/index.html) and [NumPy](https://numpy.org/doc/).

### Python Script
The python script can be found [here](https://github.com/pmodwrc/halpha/blob/main/sun_catching/alignment.py).



