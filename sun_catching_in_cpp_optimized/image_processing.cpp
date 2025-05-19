#include "image_processing.h"
#include <opencv2/opencv.hpp>
#include <opencv2/photo.hpp> //maybe not needed (from mergemertens)
#include <vector>
#include <cmath>
#include <string>
#include <numeric>
#include <iostream>
#include <ctime>  //could also use the internal pmod timeserver: server ntp1.pmodwrc.ch/ntp2.pmodwrc.ch
#include <omp.h>

/*
timing measurement:
double t0 = (double)cv::getTickCount();
//processing...
double t1 = (double)cv::getTickCount();
std::cout << "Time: " << (t1 - t0) / cv::getTickFrequency() << "s" << std::endl;
*/

//todo: performance increace: calculate LUT only all 10 Images
/*
for (size_t i = 0; i < images.size(); ++i) {
    if (i % 10 == 0) {
        // Recompute LUT here
    }
    // Apply LUT to the image
}
*/
cv::Mat apply_clip_lut(const cv::Mat& img, float min_val, float max_val) {
    // Create the LUT: a 256-element array where each value is clipped to [min_val, max_val]
    cv::Mat lut(1, 256, CV_8U);
    for (float i = 0; i < 256; ++i) {
        lut.at<float>(i) = std::min(std::max(i, min_val), max_val);   //[min,min,min..i,i,i,i,..max,max,max]
    }

    cv::Mat clipped;
    cv::LUT(img, lut, clipped);
    return clipped;
}


cv::Mat stretch_contrast(const cv::Mat& raw_image) {
    // Compute histogram
    int histSize = 50;    //todo: optimise parameter (up to 256 bins)
    float range[] = { 0, 256 };    //[0,255]
    const float* histRange[] = { range };
    cv::Mat hist;

    cv::calcHist(&raw_image, 1, 0, cv::Mat(), hist, 1, &histSize, histRange, true, false);

    /* Normalize histogram to get PDF if you want
    hist /= img.total();
    */

    // Compute cumulative distribution (CDF)
    std::vector<float> cdf(histSize, 0.0f);
    cdf[0] = static_cast<int>(hist.at<float>(0));
    for (int i = 1; i < histSize; ++i){
        cdf[i] = cdf[i - 1] + static_cast<int>(hist.at<float>(i));
    }
    //possible to speedup?
    float total = raw_image.total();


    //tresholds: 5% (0.01) on the lower end, 95% (0.999) on the upper end (0.5/0.01 = 50)
    int lower_index = 0;
    int upper_index = 0;
    for (int i = 0; i < histSize; ++i) {
        if (cdf[i] >= 0.01 * total) { lower_index = i; break; }
    }
    for (int i = histSize - 1; i >= 0; --i) {
        if (cdf[i] <= 0.999 * total) { upper_index = i; break; }
    }

    // Compute limits
    float bin_width = 256 / histSize;
    float min_val =  lower_index * bin_width;
    float max_val =  upper_index * bin_width;

    // Apply contrast stretching
    cv::Mat clipped = apply_clip_lut(raw_image,  min_val,  max_val);
    //cv::min(img, max_val, clipped);  //if LUT approach doesnt work
    //cv::max(clipped, min_val, clipped);
    
    cv::Mat stretched = (clipped - min_val) * (255 / (max_val - min_val));
    stretched.convertTo(stretched, CV_8U);  // Final 8-bit result

    return stretched;
}

/*
cv::Mat set_values_outside_radius_to_zero(const cv::Mat& image, int center_x, int center_y, int min_radius) {
    cv::Mat result = image.clone();
    for (int y = 0; y < image.rows; ++y) {
        for (int x = 0; x < image.cols; ++x) {
            double distance = std::sqrt(std::pow(x - center_x, 2) + std::pow(y - center_y, 2));
            if (distance > min_radius) {
                result.at<uchar>(y, x) = 0;
            }
        }
    }
    return result;
}

int plot_values_for_radii(const cv::Mat& image, int center_x, int center_y, int min_radius, int max_radius, int num_points) {
    std::vector<int> sums(max_radius - min_radius + 1, 0);

    for (int radius = min_radius; radius <= max_radius; ++radius) {
        int sum = 0;
        for (int i = 0; i < num_points; ++i) {
            double angle = 2 * CV_PI * i / num_points;
            int x = static_cast<int>(center_x + radius * std::cos(angle));
            int y = static_cast<int>(center_y + radius * std::sin(angle));

            if (x >= 0 && x < image.cols && y >= 0 && y < image.rows) {
                sum += image.at<uchar>(y, x);
            }
        }
        sums[radius - min_radius] = sum;
    }

    return std::distance(sums.begin(), std::min_element(sums.begin(), sums.end())) + min_radius;
}

*/

/*
optimisation: only calculate mask every 10 times
static cv::Mat mask = create_mask(image.size(), center_x, center_y, radius);
cv::Mat black;
normalized.copyTo(black, mask);*/
cv::Mat set_values_outside_radius_to_zero_mask(const cv::Mat& image, int center_x, int center_y, int radius) {
    cv::Mat mask = cv::Mat::zeros(image.size(), CV_8U);
    cv::circle(mask, cv::Point(center_x, center_y), radius, cv::Scalar(255), -1); // filled white circle, possible optimisation: only calculate mask once for all images
    cv::Mat result;
    image.copyTo(result, mask); // copy only where mask is white
    return result;
    
}

/*
more configurable colormap
cv::Mat create_halpha_colormap() {
    cv::Mat colormap(256, 1, CV_8UC3); // 256 levels, 1 column, 3 channels (BGR)
    for (int i = 0; i < 256; ++i) {
        colormap.at<cv::Vec3b>(i, 0) = cv::Vec3b(0, 0, i); // Black to red gradient
    }
    return colormap;
}
*/

//todo: look if shading is needed by comparing images with and without shading correction
cv::Mat process_image(const std::vector<cv::Mat>& images) {
    // Gaussian filtering and shadow correction, possible performance improvement: first merge images then correct, but need to test for image quality
    int N = images.size();
    std::vector<cv::Mat> corrected_images(N);

    #pragma omp parallel for
    for (size_t i = 0; i < N; ++i) {
        cv::Mat blurred, corrected, normalized; //can do cv::UMat here later
        cv::GaussianBlur(images[i], blurred, cv::Size(255, 255), 64); //cv::blus od cv::boxFilter is much faster..need to test, also values in bracket need to be odd for some odd reason
        cv::divide(images[i], blurred, corrected, 1, CV_8U);
        cv::normalize(corrected, normalized, 0, 255, cv::NORM_MINMAX, CV_8U);
        corrected_images[i] = stretch_contrast(normalized);  // Direct assignment to pre-allocated vector
    }
    // Stacking the gaus images
    cv::Mat raw_gaus_image;
    cv::Ptr<cv::MergeMertens> merge = cv::createMergeMertens();
    merge->process(corrected_images, raw_gaus_image);           // [0, 1] float output
    //cv::pow(raw_gaus_image, 1.0 / 2.2, raw_gaus_image);       // gamma correction
    raw_gaus_image *= 255.0f;                                   // scale to [0, 255]
    raw_gaus_image.convertTo(raw_gaus_image, CV_8U);            // 8-bit conversion

    //Stacking the raw images
    cv::Mat raw_image;
    merge->process(images, raw_image);      
    //cv::pow(raw_image, 1.0 / 2.2, raw_image);     //gamma correction
    raw_image *= 255.0f;                               
    raw_image.convertTo(raw_image, CV_8U);     

    //Getting the average of the to stacked images (raw and with shadow correction)
    cv::Mat mean, normalized;
    cv::addWeighted(raw_image, 0.5, raw_gaus_image, 0.5, 0.0, mean);
    cv::normalize(mean, normalized, 0, 255, cv::NORM_MINMAX, CV_8U);


    // Finding the center of the sun
    std::vector<cv::Vec3f> circles;
    cv::HoughCircles(normalized, circles, cv::HOUGH_GRADIENT, 1, 800, 10, 30, 460, 480);

    if (circles.empty()) {
        throw std::runtime_error("No circle detected in the image.");
    }

    cv::Vec3f circle = circles[0];

    int center_x = static_cast<int>(circle[0]);
    int center_y = static_cast<int>(circle[1]);

    // Setting values outside the sun to zero
    //int min_radius = plot_values_for_radii(stacked_image, center_x, center_y, 400, 600, 1000) + 20;
    //cv::Mat result = set_values_outside_radius_to_zero(stacked_image, center_x, center_y, min_radius);

    //use possibly more efficient approach to black out pixels around the sun
    int radius = static_cast<int>(circle[2]) + 30; //need to optimise the +30 parameter
    cv::Mat black = set_values_outside_radius_to_zero_mask(normalized, center_x, center_y, radius);

    //is commented out streching program in python version relevant? check with python first
    //also, if telescope is adjusted correctly, there should be no need to center the sun, so also omitted for performance


    cv::Mat normalized_image, result;
    cv::normalize(black, normalized_image, 0, 255, cv::NORM_MINMAX, CV_8U); //is normalisation needed here?
    cv::applyColorMap(normalized_image, result, cv::COLORMAP_HOT); //is this colormap sufficient?

    // Create a custom colormap (black to red gradient)
    
    /*Apply the custom colormap
    cv::Mat halpha_colormap = create_halpha_colormap();
    cv::Mat colored_image;
    cv::applyColorMap(normalized_image, colored_image, halpha_colormap);
    */


    // Adding text annotations
    //std::string date_time = "Date: " + std::to_string(2025) + "-05-06"; 
    cv::putText(result, "PMOD/WRC Davos", cv::Point(50, 50), cv::FONT_HERSHEY_SIMPLEX, 1.0, cv::Scalar(255,255,255));



    // Get the current UTC time
    std::time_t now = std::time(nullptr);
    std::tm* utc_time = std::gmtime(&now);
    char time_buffer[100];
    std::strftime(time_buffer, sizeof(time_buffer), "%Y-%m-%d %H:%M:%S UTC", utc_time);

    // Add the date and time
    std::string date_time_text = "Halpha " + std::string(time_buffer);
    cv::putText(result, date_time_text, cv::Point(1300, 50), cv::FONT_HERSHEY_COMPLEX, 1.0, cv::Scalar(255,255,255));

    cv::putText(result, "N", cv::Point(center_x, center_y - radius - 20), cv::FONT_HERSHEY_COMPLEX, 1.0, cv::Scalar(255,255,255));
    cv::putText(result, "S", cv::Point(center_x, center_y + radius + 40), cv::FONT_HERSHEY_COMPLEX, 1.0, cv::Scalar(255,255,255));
    cv::putText(result, "E", cv::Point(center_x + radius + 40, center_y), cv::FONT_HERSHEY_COMPLEX, 1.0, cv::Scalar(255,255,255));
    cv::putText(result, "W", cv::Point(center_x - radius - 40, center_y), cv::FONT_HERSHEY_COMPLEX, 1.0, cv::Scalar(255,255,255));

    return result;
    }
