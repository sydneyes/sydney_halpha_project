# Compiler
CXX = g++
BUILD ?= release

ifeq ($(BUILD),focus)
	SRCS = set_focus_in_cpp.cpp CameraControl.cpp
	TARGET = set_focus
else
	SRCS = main.cpp CameraControl.cpp alignment.cpp image_processing.cpp
	TARGET = solar_cam
endif


# Compiler flags (no optimizations here)
CXXFLAGS = -std=c++17 -pthread `pkg-config --cflags opencv4`

# Linker flags
LDFLAGS = `pkg-config --libs opencv4` -lqhyccd

# Default build rule
all: $(TARGET)

# Link rule
$(TARGET): $(SRCS)
	$(CXX) $^ -o $@ $(CXXFLAGS) $(LDFLAGS)

# Clean rule
clean:
	rm -f $(TARGET)

.PHONY: focus

focus:
	$(MAKE) BUILD=focus
