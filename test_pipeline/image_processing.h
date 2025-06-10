#ifndef IMAGE_PROCESSING_H
#define IMAGE_PROCESSING_H

#include <opencv2/opencv.hpp>
#include <vector>

cv::Mat process_image(const std::vector<cv::Mat>& images);

#endif // IMAGE_PROCESSING_H