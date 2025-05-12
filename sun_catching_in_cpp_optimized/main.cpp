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

#include <opencv2/opencv.hpp>

#include "CameraControl.h"
#include "alignment.h"
#include "image_processing.h"
//final optimisation: overclocking the raspy 5..(need better cooling tho)

const int N = 10;  //ring buffer size

std::vector<cv::Mat> ring_buffer(N);
int current_index = 0;
bool buffer_filled = false;

std::mutex buffer_mutex;
//std::condition_variable buffer_cv;
std::atomic<bool> running(true);

std::deque<std::vector<cv::Mat>> processing_queue; //could also use the more efficient std::vector<cv::Mat> if image order doesnt matter
std::mutex queue_mutex;
std::condition_variable queue_cv;

// Capture thread function
void capture_thread(CameraControl& camera, const std::vector<int>& exposure_times, int gain, int offset) {
    int i = 0;
    int exp_size = exposure_times.size();
    while (running) {
        cv::Mat image;
        int ring_index = i % N;
        int exposure_index = i % exp_size;

        if (!camera.capture_frame(exposure_times[exposure_index], gain, offset, image)) {
            std::cerr << "Capture failed at exposure index " << exposure_index << std::endl;
            continue;
        }

        // Normalize and convert to 8-bit
        cv::Mat image8bit;
        cv::normalize(image, image8bit, 0, 255, cv::NORM_MINMAX);
        image8bit.convertTo(image8bit, CV_8U);

        {
            std::lock_guard<std::mutex> lock(buffer_mutex);
            ring_buffer[ring_index] = std::move(image8bit);
            current_index = ring_index;
            if (i >= N - 1) buffer_filled = true;

            if (buffer_filled) {
                std::vector<cv::Mat> window;
                for (int j = 0; j < N; ++j) {
                    window.push_back(ring_buffer[j].clone());
                }

                std::lock_guard<std::mutex> qlock(queue_mutex);
                processing_queue.push(std::move(window));
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
            std::string output_path = "sun_halpha.png";
            cv::imwrite(output_path, result);
            std::cout << "Processed image saved to: " << output_path << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "[Thread " << id << "] Error: " << e.what() << std::endl;
        }
        images.clear();
    }
}

int main() {
    const std::string cam_id = "QHY5III200M-c8764d41ba464ec75";
    CameraControl camera;

    if (!camera.initialize()) {
        std::cerr << "Camera initialization failed." << std::endl;
        return 1;
    }

    //can probably take shorter times to improve latency
    std::vector<int> exposure_times = {500, 700, 900, 1100, 1300, 1500, 1700, 1900, 2100, 2300};
    int gain = 20;
    int offset = 6;

    int image_height = 100; //todo: get real values from set_focus optimized
    int image_width = 100;
    for (int i = 0; i < N; ++i) {
        ring_buffer[i] = cv::Mat(image_height, image_width, CV_8UC1);  //preallocate memory
    }


    std::thread cap_thread(capture_thread, std::ref(camera), exposure_times, gain, offset); //std::ref needed because std::thread passes by copy without it (exposure_times doesnt need std::ref b.c it is const reference, whitch is faster than pass by copy)

    std::vector<std::thread> processing_threads;
    for (int i = 0; i < 3; ++i) {
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
