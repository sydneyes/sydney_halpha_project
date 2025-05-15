#include <iostream>
#include <string>  
#include <thread>
#include <chrono>
#include <getopt.h>
#include <opencv2/opencv.hpp>
#include "CameraControl.h"

int main(int argc, char* argv[]){
    const std::string cam_id = "QHY5III200M-c8764d41ba464ec75";
    CameraControl camera(cam_id);

    if (!camera.initialize()) {
        std::cerr << "Camera initialization failed." << std::endl;
        return 1;
    }

    int exposure = 400;
    int refresh = 200;

    static struct option long_options[] = {
        {"exposure", required_argument, nullptr, 'e'},
        {"refresh", required_argument, nullptr, 'r'},
        {nullptr, 0, nullptr, 0}
    };

    int option_index = 0;
    int opt;
    while ((opt = getopt_long(argc, argv, "e:r:", long_options, &option_index)) != -1) {
        switch (opt) {
            case 'e':
                exposure = std::stoi(optarg);
                break;
            case 'r':
                refresh = std::stoi(optarg);
                if( refresh< 10 || refresh > 60000){
                    refresh = 200;
                }
                break;
            default:
                std::cerr << "Usage: ./set_focus --exposure <value> --refresh<value>\n";
                return 1;
        }
    }

    int gain = 20;
    int offset = 6;
    cv::Mat image;
    for(int i = 0; i < 50000; ++i){     
        camera.capture_frame(exposure, gain, offset, image);
        std::string output_path = "/home/pi/docs/sydney_halpha_project/api_cpp/images/test_focus.png"; //is .tiff better?
        cv::imwrite(output_path, image);
        std::this_thread::sleep_for(std::chrono::milliseconds(refresh));
    }
    camera.close();
    return 0;
}
