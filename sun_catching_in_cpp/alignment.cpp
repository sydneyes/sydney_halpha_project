#include "alignment.h"
#include <opencv2/opencv.hpp>
#include <vector>
#include <iostream>
#include <fstream>
#include <stdexcept>

//calulate shift based on first image
std::vector<cv::Point2f> calculate_shifts(const std::vector<cv::Mat>& raw_data, const std::string& log_file_path) {
    std::vector<cv::Point2f> centers;

    for (const auto& image : raw_data) {
        std::vector<cv::Vec3f> circles;
        cv::HoughCircles(image, circles, cv::HOUGH_GRADIENT, 1, 800, 10, 30, 460, 480);

        if (circles.empty()) {
            std::ofstream log_file(log_file_path, std::ios::app);
            log_file << "Error: Telescope not focused properly or no circles detected.\n";
            throw std::runtime_error("Telescope not focused properly or no circles detected.");
        }

        cv::Point2f center(circles[0][0], circles[0][1]);
        centers.push_back(center);
    }

    //calulate shift based on first image (can be improved by taking average)
    std::vector<cv::Point2f> shifts(centers.size());
    for (size_t i = 0; i < centers.size(); ++i) {
        shifts[i] = centers[i] - centers[0];
    }

    return shifts;
}

//align images based on calculated shifts with warpAffine.
// Because the input image (stored in raw_data) is normalised, the output image (stored in shifted_image) is also already normalized.
std::vector<cv::Mat> align_images(const std::vector<cv::Mat>& raw_data, const std::vector<cv::Point2f>& shifts) {
    std::vector<cv::Mat> shifted_images;

    for (size_t i = 0; i < raw_data.size(); ++i) {
        cv::Mat shifted_image;
        cv::Mat translation_matrix = (cv::Mat_<float>(2, 3) << 1, 0, -shifts[i].x, 0, 1, -shifts[i].y);
        cv::warpAffine(raw_data[i], shifted_image, translation_matrix, raw_data[i].size());
        shifted_images.push_back(shifted_image);
    }

    return shifted_images;
}