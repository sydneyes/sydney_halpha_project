#include "CameraControl.h"
#include <iostream>
#include <string>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <qhyccd.h>
#include <opencv2/opencv.hpp>

class CameraControl {
public:
    CameraControl(const std::string& camera_id)
        : camhandle(nullptr), camera_id(camera_id) {}

    bool initialize() {
        if (InitQHYCCDResource() != QHYCCD_SUCCESS) return false;

        if (ScanQHYCCD() <= 0) return false;

        char id[256] = {0};
        if (GetQHYCCDId(0, id) != QHYCCD_SUCCESS) return false;

        std::cout << "Found camera: " << id << std::endl;

        camhandle = OpenQHYCCD(const_cast<char*>(camera_id.c_str()));
        if (!camhandle) return false;

        SetQHYCCDReadMode(camhandle, 0);
        SetQHYCCDStreamMode(camhandle, 0);

        if (InitQHYCCD(camhandle) != QHYCCD_SUCCESS) return false;

        return true;
    }

    bool capture_frame(double exposure_us, double gain, double offset, cv::Mat& output_image) {
        SetQHYCCDParam(camhandle, CONTROL_EXPOSURE, exposure_us);
        SetQHYCCDParam(camhandle, CONTROL_GAIN, gain);
        SetQHYCCDParam(camhandle, CONTROL_OFFSET, offset);
        SetQHYCCDParam(camhandle, CONTROL_TRANSFERBIT, 16);

        double chipw, chiph, pixelw, pixelh;
        uint32_t w, h, bpp;
        if (GetQHYCCDChipInfo(camhandle, &chipw, &chiph, &w, &h, &pixelw, &pixelh, &bpp) != QHYCCD_SUCCESS) {
            return false;
        }

        SetQHYCCDBinMode(camhandle, 1, 1);
        SetQHYCCDResolution(camhandle, 0, 0, w, h);

        uint32_t channels;
        uint32_t image_size = w * h * (bpp / 8);
        std::vector<uint8_t> buffer(image_size);

        if (ExpQHYCCDSingleFrame(camhandle) != QHYCCD_SUCCESS) return false;

        int ret = GetQHYCCDSingleFrame(camhandle, &w, &h, &bpp, &channels, buffer.data());
        if (ret != QHYCCD_SUCCESS) return false;

        // Convert to OpenCV image
        if (bpp == 16) {
            output_image = cv::Mat(h, w, CV_16UC1, buffer.data()).clone();  // Clone to own memory
        } else if (bpp == 8) {
            output_image = cv::Mat(h, w, CV_8UC1, buffer.data()).clone();
        } else {
            std::cerr << "Unsupported bit depth: " << bpp << std::endl;
            return false;
        }

        return true;
    }

    void close() {
        if (camhandle) {
            CloseQHYCCD(camhandle);
            camhandle = nullptr;
        }
        ReleaseQHYCCDResource();
    }

    ~CameraControl() {
        close();
    }

private:
    qhyccd_handle* camhandle;
    std::string camera_id;
};
