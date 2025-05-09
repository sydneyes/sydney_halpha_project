#include <iostream>
#include <string>  
#include <thread>
#include <chrono>
#include <opencv2/opencv.hpp>
#include "CameraControl.h"

int main(){
    const std::string cam_id = "QHY5III200M-c8764d41ba464ec75";
    CameraControl camera(cam_id);

    if (!camera.initialize()) {
        std::cerr << "Camera initialization failed." << std::endl;
        return 1;
    }

    std::cout<< "what exposure time do you want? (if you dont know, start with 400)";
    int exposure_time;
    std::cin>> exposure_time;
    int gain = 20;
    int offset = 6;
    cv::Mat image;
    for(int i = 0; i < 500; ++i){     
        camera.capture_frame(exposure_time, gain, offset, image);
        std::string output_path = "test_focus.tiff";
        cv::imwrite(output_path, image);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    camera.close();
    return 0;
}
