# Image Processing
This script is for image processing. It takes pictures of the sun with different exposure times edits them and merges them together afterwards. In the end it colors the final image and labels it with time and location

### Code Description
In this part of the documentation the code is split up in the different section of the image processing. 

#### Shading Correction

The shading correction is needed because our telescope produces a shading on the images that are delievered from the camera. Like you can see ![Image with shadows](https://github.com/pmodwrc/halpha/blob/main/sun_catching/Raw_images/sun_halpha_0.tiff)

First of all we run a Gaussian Kernel with a big size and a high sigma in the spatial domain. With this Kernel we blurr the image so far that we only get the shadows remaining in our new image. The Kernel is applied with the `filter2d` function from `cv2`.

```python
gaussian_kernel = cv2.getGaussianKernel(kernel_size, sigma)
gaus = cv2.filter2D(img, cv2.CV_8U, kernel=gaussian_kernel_2d)
```

The parameters have the following meaning:

- `kernel_size`: Choosing the size of the Kernel. We took for example 256 so that the kernel is big enough for sure and only the pattern of the shadow remains.

- `sigma`: Sigma is the Gaussian standart deviation


Afterwards the original image is divided by its shadow pattern to get a shadow corrected image

#### Histogramm stretching

To obtain to complete dynamic range from 0 to 255 the histogramm is stretched with the following formula:

$$
\frac{{(\text{sharpened} - \text{min_value}) \cdot (\text{new_max} - \text{new_min})}}{{\text{max_value} - \text{min_value}} + \text{new_min}}
$$

The parameters are determined as follows:

- `sharpened`: This ist the image which you wanna stretch over the whole dynamic range.

- `min_value` and `max_value`: This are values which determine the range of the histogramm with values that are important for the stretching of the histogramm.

- `new_min` and `new_max`: This values represent the new range of the histogramm: mostly they are set to `0` and `255` because this represents the whole dynamic range.

This function is used several times to not loose any structure while processing the image. For example after cutting out the sun the histogram stretching is applied to highlight the structure of the border and the inside of the sun.

#### Getting the peaks of the histogramm

To get the sections with important structures you try to extract the parts of the histogram where it has a peak. We do this with analysing the CDF function of the histogram. We extract the parts where the CDF function doesn't change more than a certain value. 

Image with histogram and cdf function


#### Merging the images

To merge the images with different exposure times we use the Algorithm from Mertens. To process the images With the function `MergeMertens.process` from `cv2` you have to give the function a list with differently exposed images and the images will be stacked. 

```python
compensator = cv2.createMergeMertens()
data_image = compensator.process(gaus_images)
```
In our case we use the MergeMertens to firstly stack the raw images and secondly stack the images with the shadow correction. Afterwards we take the mean of this to images to ensure that the values of the image are not to high nor to low.

Image to visualise the effect of taking the mean

#### Cutting out the sun

To make sure that everything outside the sun is set to 0 we calculate the center with the `HoughCircles` function like done in the [Alignment](https://github.com/pmodwrc/halpha/blob/main/docs/reference/alignment.md)

Afterwards you determine the radius where the sun ends with the function plot_values_for_radii. This is then used to set every value outside this radius to 0.


#### Coloring the Image 

To color our image in Halpha we used the command `LinearSegmentedColormap` from Matplotlib with which you can make a personalised Colormap.

```python
cmap = LinearSegmentedColormap.from_list('halpha_cmap', ['black', 'red'], N=256)
```

In our case we made it from black to red because we our making images of the sun in the Halpha wavelenght.

#### Labeling the image

To give the images a more scientific look we labeled them with the positions of the poles, the location and the time when the image was taken. We labeled them with the `write_text`function which uses the `putText` function from `cv2`


### Usage 

This image processing script is mainly used in our application for the livestream. It follows the alignment of the raw images. The whole script for the livetstream can be found [here](https://github.com/pmodwrc/halpha/blob/main/sun_catching/image_processing.py)

## Reference

#### Sources
The idea of the shadow correction with a Gaussian Kernel and the following Division is taken from pages 173 and 174 of:
- Rafael C. Gonzalez, Richard E. Woods 2018, *Digitale Image Processing Fourth edition, Pearson*

The functions where mainly build with [OpenCV](https://docs.opencv.org/4.x/index.html), [NumPy](https://numpy.org/doc/), [Matplotlib](https://matplotlib.org/stable/index.html).

#### Python Script
The python script can be found [here](https://github.com/pmodwrc/halpha/blob/main/sun_catching/image_processing.py)



