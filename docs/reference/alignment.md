# Alignment
This Script is to shift the images so that the sun in the different images is aligned. We have to do the aligment of the images to get better results in the following image processing steps. 

Despite the fact that the telescope is located on a tracking device there are shifts of the sun in the different images

### Code Description
The function for the aligment is separated in 3 steps: 

1. The centers of the sun images are located in the first part using the `HoughCircles` function from `cv2`:

    ```python
    circles = cv2.HoughCircles(im, cv2.HOUGH_GRADIENT, dp=1, minDist=800, param1=10, param2=30, minRadius=470, maxRadius=480)
    ```
    The Parameters have the following values:
   - `dp=1`: Inverse ratio of the accumulator resolution to the image resolution. It defines the accumulator resolution as dp pixels in the input image.
   - `minDist=800`: Minimum distance between the centers of the detected circles. If the distance between two circle centers is less than this value, only the stronger one is retained.
   - `param1=10`: The higher threshold of the two passed to the Canny edge detector. It is used for edge gradient detection in the image.
   - `param2=30`: Accumulator threshold for circle detection. It is a lower threshold for circle detection, meaning a circle needs to have at least this value in the accumulator to be considered as a candidate.
   - `minRadius=470`: Minimum radius of the circles to be detected. This is chosen to speed up the algorithm and don't run over every circle from Radius 0.
   - `maxRadius=480`: Maximum radius of the circles to be detected. This is chosen to speed up the algorithm and don't run over every circle from Radius 0.



2. In the second step the shift of the images is calculated based on the center of the first image.

3. In the end the images are shifted with the function warpAffine from cv2.
    ```python
    cv2.warpAffine(image, M, (cols, rows))
    ```
    The parameters have the following values:
    - `image`: The input image to be transformed.

    - `M`: The 2x3 transformation matrix representing the geometric transformation to be applied. It defines how each point in the original image will be mapped to its new position in the output image. You get this Matrix by taking the values that you calculated before in the second step.

    - `(cols, rows)`: The size of the output image, specified as a tuple (width, height). It determines the dimensions of the result after the geometric transformation.



### Usage 
This function for the aligment is mainly used in a script where we take images with different exposure times and merge them later together to make a livestream. This can be found [here](https://github.com/pmodwrc/halpha/blob/main/sun_catching/process.py).

## Reference

### Sources
The function was build with [OpenCV](https://docs.opencv.org/4.x/index.html) and [NumPy](https://numpy.org/doc/).

### Python Script
The python script can be found [here](https://github.com/pmodwrc/halpha/blob/main/sun_catching/alignment.py).



