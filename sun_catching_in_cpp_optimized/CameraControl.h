#ifndef CAMERA_CONTROL_H
#define CAMERA_CONTROL_H

#include <string>
#include <opencv2/opencv.hpp>
#include <qhyccd.h>

class CameraControl {
public:
    CameraControl(const std::string& camera_id);
    ~CameraControl();

    bool initialize();
    bool capture_frame(double exposure_us, double gain, double offset, cv::Mat& output_image);
    void close();

private:
    qhyccd_handle* camhandle;
    std::string camera_id;
};

#endif // CAMERA_CONTROL_H