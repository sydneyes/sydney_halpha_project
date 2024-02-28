# Uploading your Image to a Webserver

To upload the images to a Webserver this script uses the [subprocess](https://docs.python.org/3/library/subprocess.html) library to access the shell fom the RaspberryPi and perform the following command.

```
/usr/bin/smbclient "//ad.pmodwrc.ch/Institute" --user=web.service@ad.pmodwrc.ch%SCRLvugFhi0dKu7K5XnF --workgroup=AD.pmodwrc.ch --command "cd Infrastructure/WWW/www.pmodwrc.ch/htdocs/images/halpha; put sun.PNG"

```
This command uploads the image which is saved as `sun.PNG` to this [site](https://www.pmodwrc.ch/images/halpha/sun.PNG).

!!! Important
    It is important to locate the file which you want to upload in the same folder as your Python Script that uses this function.

#### Python Script
The Python script can be found [here](https://github.com/pmodwrc/halpha/blob/main/sun_catching/upload_image.py).