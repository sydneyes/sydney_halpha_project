# Camera Driver

In the python code we used the offical wrapper for the sdk from [QHYCCD](https://pypi.org/project/qcam-sdk/) which you can pip install. The underlying binary files that gets called from the python library we got from here the [official release page](https://www.qhyccd.com/html/prepub/log_en.html#!log_en.md). 


Since the version from 24.01.09 did not work for us we had to get support over the offical email channel. Where we got support from [QinXiaoXu](qxx@qhyccd.com) which recompiled us the binaries for our target and send us the [download link](https://www.qhyccd.com/file/repository/latestSoftAndDirver/other/libqhyccd_20240118_noopencv.tar ). 


**Thanks again for the support QinXiaoXu!:heart:**

To install the driver we followed the original description supplied if you download the sdk. Look at the example in our [Installation from scratch](../../installation-guide/install-scratch/) guide.

### Python Script
The python script can be found [here](https://github.com/pmodwrc/halpha/blob/main/sun_catching/CameraControl.py).