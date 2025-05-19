#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <opencv2/opencv.hpp>
#include <getopt.h>

#include "CameraControl.h"
#include "alignment.h"
#include "image_processing.h"

std::mutex cam_mutex;  // Shared camera access lock

//performance improvement: memory allocation


//take images with camera
void capture_images(int n, const std::vector<int>& exposure_times, int gain, int offset, CameraControl& camera, std::vector<cv::Mat>& images) {
    for (int i = 0; i < n; ++i) {
        cv::Mat image;

        {
            std::lock_guard<std::mutex> lock(cam_mutex);  // Ensure thread-safe access
            if (!camera.capture_frame(exposure_times[i], gain, offset, image)) {
                std::cerr << "Failed to capture frame " << i << std::endl;
                return;
            }
        }

        // Normalize and convert to 8-bit
        cv::Mat image8bit;
        cv::normalize(image, image8bit, 0, 255, cv::NORM_MINMAX);
        image8bit.convertTo(image8bit, CV_8U);

        // Save raw image
        //std::string filename = "raw_frame_" + std::to_string(i) + ".tiff";
        //cv::imwrite(filename, image8bit);
        images.push_back(image8bit);
    }
}

int main() {
    const std::string cam_id = "QHY5III200M-c8764d41ba464ec75";
    CameraControl camera(cam_id);

    if (!camera.initialize()) {
        std::cerr << "Camera initialization failed." << std::endl;
        return 1;
    }

    const int n = 10;
    //can probably take shorter times to improve latency
    std::vector<int> exposure_times = {400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200};
    int gain = 20;
    int offset = 6;

    //capture 10 images
    std::vector<cv::Mat> images;
    capture_images(n, exposure_times, gain, offset, camera, images);

/*
    if (images.size() != n) {
        std::cerr << "Failed to capture all frames." << std::endl;
        return 1;
    }
*/

    //calculate shifts
    std::string log_file_path = "error_log.txt";
    std::vector<cv::Point2f> shifts;
    try {
        shifts = calculate_shifts(images, log_file_path);
    } catch (const std::exception& e) {
        std::cerr << "Alignment error: " << e.what() << std::endl;
        return 1;
    }

    //align images
    std::vector<cv::Mat> aligned_images = align_images(images, shifts);

    // Process aligned images
    cv::Mat processed_image;
    try {
        processed_image = process_image(aligned_images);
    } catch (const std::exception& e) {
        std::cerr << "Image processing error: " << e.what() << std::endl;
        return 1;
    }

    // Save the final processed image
    std::string output_path = "/home/pi/docs/sydney_halpha_project/api_cpp/images/sun_halpha.png";
    cv::imwrite(output_path, processed_image);
    std::cout << "Processed image saved to: " << output_path << std::endl;

    return 0;
}
