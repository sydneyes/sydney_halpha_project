#ifndef ALIGNMENT_H
#define ALIGNMENT_H

#include <opencv2/opencv.hpp>
#include <vector>
#include <string>

std::vector<cv::Point2f> calculate_shifts(const std::vector<cv::Mat>& raw_data, const std::string& log_file_path);
std::vector<cv::Mat> align_images(const std::vector<cv::Mat>& raw_data, const std::vector<cv::Point2f>& shifts);

#endif // ALIGNMENT_H