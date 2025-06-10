#include "alignment.h"
#include <opencv2/opencv.hpp>
#include <vector>
#include <iostream>
#include <fstream>
#include <stdexcept>
#include <omp.h>

//calulate shift based on first image
std::vector<cv::Point2f> calculate_shifts(const std::vector<cv::Mat>& raw_data, const std::string& log_file_path) {
    int N = raw_data.size();
    std::vector<cv::Point2f> centers(N);
    #pragma omp parallel for
    for (size_t i = 0; i < raw_data.size(); ++i) {
        cv::Mat image = raw_data[i];
        std::vector<cv::Vec3f> circles;
        cv::Mat resized_image;
        cv::resize(image, resized_image, cv::Size(image.cols / 2, image.rows / 2));  //downscale by 50% to speed up cv::HoughCircles (maybe less % possible?)
        cv::HoughCircles(resized_image, circles, cv::HOUGH_GRADIENT, 1, 800, 10, 30, 230, 240);
        
        if (!circles.empty()) {
            cv::Point2f center(circles[0][0] * 2, circles[0][1] * 2);
            centers[i] = center;
        }
    }

    //calulate shift based on first image (can be improved by taking average)!!:
    /*
    cv::Point2f mean_center(0.f, 0.f);
for (const auto& c : centers) mean_center += c;
mean_center *= 1.0f / centers.size();

for (size_t i = 0; i < centers.size(); ++i) {
    shifts[i] = centers[i] - mean_center;
} now omitted bc i want to test first
    */
    std::vector<cv::Point2f> shifts(centers.size());
    for (size_t i = 0; i < centers.size(); ++i) {
        shifts[i] = centers[i] - centers[0];
        //consider std::round for speedup for slight precision loss
    }

    return shifts;
}

//align images based on calculated shifts with warpAffine.
// Because the input image (stored in raw_data) is normalised, the output image (stored in shifted_image) is also already normalized.
std::vector<cv::Mat> align_images(const std::vector<cv::Mat>& raw_data, const std::vector<cv::Point2f>& shifts) {
    int N = raw_data.size();
    std::vector<cv::Mat> shifted_images(N);

    #pragma omp parallel for
    for (size_t i = 0; i < N; ++i) {
        cv::Mat shifted_image;
        cv::Mat translation_matrix = (cv::Mat_<float>(2, 3) << 1, 0, -shifts[i].x, 0, 1, -shifts[i].y);
        cv::warpAffine(raw_data[i], shifted_image, translation_matrix, raw_data[i].size());
        
        // Directly assign to the corresponding index in the vector
        shifted_images[i] = shifted_image;
    }

    return shifted_images;
}