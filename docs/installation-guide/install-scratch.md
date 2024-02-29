
# Starting from Scratch
Assuming you use a Raspberry Pi 5. If you have some other hardware this steps may differ but still can be a usefull reference on what is needed.
Requirements:

- A Raspberry Pi 5 (R-Pi)
- A microSD card (16GB or larger recommended)
- A microSD card reader
- The pre-configured HAlpha image file. You will find the latest release in the source repo.
- Imaging software [Raspberry Pi Imager](https://www.raspberrypi.com/software/)

### Write image Steps
1. Open Raspberry Pi Imager.
2. Plug your sd card with your sd card reader to your computer.
3. Under `Raspberry Pi Device` select `Raspberry Pi 5`.
4. Under `Operating System`, under the menu `Raspberry Pi OS(other)` select `Raspberry Pi OS Lite (64-bit)`.
5. Under `Storage` choose you sd card.
6. Press `ctrl`+`shift`+`x` to open the OS Customisation menu. Under menu GENERAL do the following:
    - Unset the hostname
    - Set a username and password (for example username: pi and password: raspberry) you can also later change it with cmd `passwd`
    - If you connect over ethernet unset Wireless
    - Set your keyboard layout
![OS menu](../images/pi-imager-menu1.png)
7. Under SERVICES do the following:
    - Enable SSH 
    - Enable Use password authentication
![OS menu](../images/pi-imager-menu2.png)
8.  OS Customisation menu and press `next`.
9.  For the question `Would you like to apply OS customisation settings?` press yes. 
10.  Press again yes for formatting the sd  card. Then the image getts written to your sd card. (It can take some minutes.)
11.  Once the image is finished take the sd card and plug it into the unpowered Raspberry pi sd card slot.


### Get the source code
Once you have flashed the sd card you can plugin a keyboard, network cable and display to the raspberry pi and power it up. Now you should see a black starting screen loading up. 
Once finished it will ask to login with your prevvios set username and password.
1. Login using the username password we created in the imager
2. Get the hostname of the R-Pi with the command
```bash title="terminal"
pi@raspberrypi:~$ hostname -I
```
This will give you back the ip4 adress of your RP5.
```bash title="terminal output"
pi@raspberrypi:~$ hostname -I
172.16.10.250 2001:620:1b0:a:2895:867f:fead:9f52
```
Know we can use the ip4 adress to ssh into our R-Pi from within the same network
```bash title="cmd on your pc"
C:\Users\cedric.renda>ssh pi@172.16.10.250
```
!!!tip 
    if you already had an ssh connection under this ip4 address you will get an error:
    ```bash
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    ...
    ```
    to resolve this just navigate to the /.ssh folder and delete all the entries of this ip4 address from known_hosts file.

#### Install git
Now we have to install git to get the source code from the repo. To do this we first update the R-Pi and then install git:
```bash title="ssh terminal"
pi@raspberrypi:~ $ sudo apt-get update
pi@raspberrypi:~ $ sudo apt-get upgrade
pi@raspberrypi:~ $ sudo apt-get install git
```
Now we clone the source code from our repo. For this we create a directory in our home with 
```bash title="ssh terminal"
pi@raspberrypi:~ $ mkdir /home/pi/docs
pi@raspberrypi:~ $ cd docs
pi@raspberrypi:~ $ git clone https://github.com/pmodwrc/halpha.git
pi@raspberrypi:~ $ cd halpha
```
Now we sucessfully cloned the source repo! :fire: