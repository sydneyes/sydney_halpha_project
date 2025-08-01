#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <chrono>
#include <ctime>
#include <getopt.h>
#include <opencv2/opencv.hpp>

#include "CameraControl.h"
#include "alignment.h"
#include "image_processing.h"
//final optimisation: overclocking the raspy 5..(need better cooling tho)

//todo: try flags -ffast-math, flto

bool buffer_filled = false;
std::mutex buffer_mutex; //maybe not needed: current program maybe already thread safe for buffer
//std::condition_variable buffer_cv;
std::atomic<bool> running(true);

std::deque<std::vector<cv::Mat>> processing_queue; //could also use the more efficient std::vector<cv::Mat> if image order doesnt matter
std::mutex queue_mutex;
std::mutex save_mutex;
std::condition_variable queue_cv;

// Capture thread function
void capture_thread(CameraControl& camera, const std::vector<int>& exposure_times, int gain, int offset, int nimages, std::vector<cv::Mat>& ring_buffer) {
    int i = 0;
    while (running) {
        cv::Mat image;
        int ring_index = i % nimages;

        if (!camera.capture_frame(exposure_times[ring_index], gain, offset, image)) {
            std::cerr << "Capture failed at ring index " << ring_index << std::endl;
            continue;
        }

        // Normalize and convert to 8-bit
        cv::Mat image8bit; //could use cv::UMat for GPU acceleration
        cv::normalize(image, image8bit, 0, 255, cv::NORM_MINMAX);
        image8bit.convertTo(image8bit, CV_8U);

        {
            std::lock_guard<std::mutex> lock(buffer_mutex);
            image8bit.copyTo(ring_buffer[ring_index]);
            if (i >= nimages - 1) buffer_filled = true;

            if (buffer_filled) {
                std::vector<cv::Mat> window(nimages);
                for (int j = 0; j < nimages; ++j) {
                    window[j] = ring_buffer[j].clone();
                }

                std::lock_guard<std::mutex> qlock(queue_mutex);
                processing_queue.push_back(std::move(window));
                queue_cv.notify_one();
            }
        }

        ++i;
        std::this_thread::sleep_for(std::chrono::milliseconds(10)); //control frame rate
    }
}

//worker thread function
void processing_worker(int id) {
    std::vector<cv::Mat> images;
    while (running) {

        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            queue_cv.wait(lock, [] { return !processing_queue.empty() || !running; });

            if (!running && processing_queue.empty()) break;

            images = std::move(processing_queue.front());
            processing_queue.pop_front();
        }

        try {
            auto shifts = calculate_shifts(images, "error_log.txt");
            auto aligned = align_images(images, shifts);
            auto result = process_image(aligned);

            // Save the final processed image
            std::string output_path = "/home/pi/docs/sydney_halpha_project/api_cpp/images/sun_halpha.png";
            std::lock_guard<std::mutex> lock(save_mutex);  //not shure if this mutex is really necessary
            cv::imwrite(output_path, result);
            std::cout << "Processed image saved to: " << output_path << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "[Thread " << id << "] Error: " << e.what() << std::endl;
        }
        images.clear();
    }
}

int main(int argc, char* argv[]) {
    const std::string cam_id = "QHY5III200M-c8764d41ba464ec75";
    CameraControl camera(cam_id);

    if (!camera.initialize()) {
        std::cerr << "Camera initialization failed." << std::endl;
        return 1;
    }
    std::cout<<"testtesttest";

  
    int threads = 3;
    int exposure = 400;
    int nimages = 10;

    static struct option long_options[] = {
        {"threads", required_argument, nullptr, 't'},
        {"exposure", required_argument, nullptr, 'e'},
        {"nimages", required_argument, nullptr, 'n'},

        {nullptr, 0, nullptr, 0}
    };

    int option_index = 0;
    int opt;
    while ((opt = getopt_long(argc, argv, "t:e:n:", long_options, &option_index)) != -1) {
        switch (opt) {
            
            case 't':
                threads = std::stoi(optarg);
                if(threads < 1 || threads > 16){ //for the funny people...
                    threads = 3;
                }
                break;
            case 'e':
                exposure = std::stoi(optarg);
                break;
            case 'n':
                nimages = std::stoi(optarg);
                if(nimages < 1 || nimages > 1000){
                    nimages = 10;
                }
                break;
            default:
                std::cerr << "Usage: ./solar_cam  --threads <value> --exposure <value> --nimage<value>\n";
                return 1;
        }
    }

    //can probably take shorter times to improve latency
    
    std::vector<int> exposure_times(nimages);
    for(int i = 0; i < nimages; ++i){
        exposure_times[i] = exposure + 200 * i;
    }
    int gain = 20;
    int offset = 6;

    int image_height = 1080;
    int image_width = 1920;
    std::vector<cv::Mat> ring_buffer(nimages);
    for (int i = 0; i < nimages; ++i) {
        ring_buffer[i].create(image_height, image_width, CV_8UC1);  //preallocate memory
    }


    std::thread cap_thread(capture_thread, std::ref(camera), exposure_times, gain, offset, nimages, std::ref(ring_buffer)); //std::ref needed because std::thread passes by copy without it (exposure_times doesnt need std::ref b.c it is const reference, whitch is faster than pass by copy)

    std::vector<std::thread> processing_threads;
    for (int i = 0; i < threads; ++i) {
        processing_threads.emplace_back(processing_worker, i);
    }

    //shutdown on ENTER key
    std::cout << "Running... Press ENTER to stop.\n";
    std::cin.get();

    running = false;
    queue_cv.notify_all();

    cap_thread.join();
    for (auto& t : processing_threads) t.join();

    std::cout << "Shutdown complete.\n";
    return 0;
}
