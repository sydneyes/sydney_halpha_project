# Remote access - GUI
The script [livestream_gui.py](https://github.com/pmodwrc/halpha/blob/main/GUI/livestream_gui.py) is meant to build an easy controllable interface to start and stop the livestream. Furthermore it also displays the most common errors that occur on the [livestream.py](https://github.com/pmodwrc/halpha/blob/main/sun_catching/livestream.py) script is running. 

## Code Description
The first thing that the code does is to check wheter the interface is already running or not. This check is done by checking wether a lockfile exists or not. When it doesn't exist it is created to prevent from opening more than one Interface.

Afterwards a window with an interface is created with the [Tkinter library](https://docs.python.org/3/library/tkinter.html). The interface displays the status of the livestream, a button to start or stop the livestream and it shows errors that occur on the RaspberryPi. All this functions are controlled over SSH with the [Paramiko library](https://www.paramiko.org/).

### Status display
To get the status of the livetsream the following comamnd is executed in the terminal of the RaspberryPi over SSH.

```
command = f"ps aux | grep {script_name}"   

```

### Start and Stop Button
The following commands are executed to start and stop the livestream.

#### Start command
```
command = "source /home/pi/docs/halpha/venv/bin/activate && python /home/pi/docs/halpha/sun_catching/livestream.py"
```
This activates the virtual environement and executes the desired script
#### Stop command
```
ssh.exec_command(f"pkill -f 'python /home/pi/docs/halpha/sun_catching/livestream.py'")
```
This simply kills all processes assigned to the livestream.py script.

### Error handling
To handle the errors that occur in the livetsream.py script they are written into a logfile on the RaspberryPi. This file can then be read over an SFTP connection with the RaspberryPi with the following structure.
```python
    with sftp.file("/home/pi/docs/halpha/sun_catching/error_log.txt", 'r') as file:
        file_contents = file.read()
    error_status.config(text = file_contents)
```

## Installation
To use this interface on a remote machine Python should be installed on the remote machine and the following librarys have to be installed over pip:

- Paramiko
- Tkinter

## Python script
The python script can be found [here](https://github.com/pmodwrc/halpha/blob/main/GUI/livestream_gui.py).

