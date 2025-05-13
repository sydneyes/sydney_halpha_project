CXX = g++
BUILD ?= release

ifeq ($(BUILD),focus)
	SRCS = set_focus_in_cpp.cpp CameraControl.cpp
	CXXFLAGS = -std=c++17 -pthread `pkg-config --cflags opencv4`
	TARGET = set_focus
else ifeq ($(BUILD),native)
	SRCS = main.cpp CameraControl.cpp alignment.cpp image_processing.cpp
	CXXFLAGS = -O3 -fopenmp -march=native -funroll-loops -std=c++17 -pthread `pkg-config --cflags opencv4`
	TARGET = solar_cam
else
	SRCS = main.cpp CameraControl.cpp alignment.cpp image_processing.cpp
	CXXFLAGS = -O3 -fopenmp -march=armv8-a -funroll-loops -std=c++17 -pthread `pkg-config --cflags opencv4`
	TARGET = solar_cam
endif


LDFLAGS = -fopenmp `pkg-config --libs opencv4` -lqhyccd


OBJS = $(SRCS:.cpp=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) -o $@ $^ $(LDFLAGS)

%.o: %.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS)

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: focus native

focus:
	$(MAKE) BUILD=focus

native:
	$(MAKE) BUILD=native


