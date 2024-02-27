# Spectral Operations (spectral_ops)

## Overview

The `spectral_ops` subpackage provides tools for performing spectral analysis and manipulation, specifically focusing on the convolution of spectral data with slit functions. This subpackage is designed to facilitate the preprocessing and analysis of spectral data by applying mathematical transformations that mimic the effects of instrumental slit functions on measured spectra.

## Features

- **Convolution with Slit Functions**: Apply a specified slit function to spectral data, simulating the instrumental broadening effects.
- **Support for Equidistant and Non-Equidistant Spectral Data**: Functions within the subpackage can handle both equidistant and non-equidistant spectral wavelength grids, providing flexibility for various types of spectral data.
- **Spline Representation for Slit Functions**: Utilize spline representations (specifically, `PPoly` objects from SciPy) to define slit functions, allowing for precise and customizable convolution operations.


## Reference

To use the `spectral_ops` subpackage, import the desired function(s) and pass your spectral data along with the slit function spline. Ensure your spectral data and slit function are prepared according to the function requirements, particularly regarding the equidistance of wavelength grids and the spline representation of the slit function.



## Examples

```python
from spectral_ops import conv_spec_with_slit
import numpy as np
from scipy.interpolate import CubicSpline

# Example spectral data and slit function
spec_wavelengths = np.linspace(400, 700, 300)
spec_intensities = np.sin(2 * np.pi * spec_wavelengths / 100) + 0.5
output_wavelengths = np.linspace(400, 700, 150)
x = np.linspace(-5, 5, 100)
y = np.exp(-x**2)
slit_spline = CubicSpline(x, y)

# Perform convolution
convolved_intensities = conv_spec_with_slit(spec_wavelengths, spec_intensities, output_wavelengths, slit_spline)
```

For detailed examples and advanced usage, refer to the function documentation within the subpackage.

---

This README template provides a basic introduction to the `spectral_ops` subpackage, its mathematical foundations, and a simple usage example. You can expand this documentation with more specific examples, installation instructions, and any dependencies or prerequisites as needed for your package.

## MATH

The main mathematical operation performed by this subpackage is the convolution of spectral data with a specified slit function. Convolution is a mathematical operation that produces a new function showing how the shape of one function is modified by the other. In the context of spectral analysis, convolution with a slit function simulates how an instrument's finite resolution broadens the spectral lines.

### Convolution Operation

Given a spectrum \(I(\lambda)\) and a slit function \(S(\lambda)\), the convolution operation is defined as:

\[ I'(\lambda) = (I * S)(\lambda) = \int_{-\infty}^{\infty} I(\lambda') S(\lambda - \lambda') d\lambda' \]

where \(I'(\lambda)\) is the convolved spectrum, showing the instrumental broadening effect on the original spectral data.

### Spline Representation of Slit Functions

Slit functions are represented using spline interpolation (specifically, piecewise polynomials or `PPoly` in SciPy), which allows for a flexible and accurate description of the slit function's shape. This representation is crucial for simulating various instrumental profiles accurately.

### Handling of Equidistant and Non-Equidistant Grids

The subpackage accommodates both equidistant and non-equidistant spectral grids by adjusting the convolution process accordingly. For non-equidistant grids, additional steps such as interpolation are performed to ensure the convolution operation accurately reflects the instrumental effects on the spectral data.