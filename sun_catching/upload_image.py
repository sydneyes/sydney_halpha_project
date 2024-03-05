import subprocess
import os


user = os.getenv("SAMBA_USER", "web.service")
password = os.getenv("SAMBA_PASSWORD", "PEnn2moSPvMLboU5HCPe")
path_to_client = "/usr/bin/smbclient"
path_to_target = "//ad.pmodwrc.ch/Institute"
workgroup = "AD.pmodwrc.ch"
cmd = "cd Infrastructure/WWW/www.pmodwrc.ch/htdocs/images/halpha; put sun.PNG"

def run_smbclient():
    command = [
        path_to_client,
        path_to_target,
        f"--user={user}%{password}",
        f"--workgroup={workgroup}",
        "--command",
        cmd  
    ]

    try:
        subprocess.run(command, check=True)
        print("Image uploaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Image couldn't be uploaded")
        print("check the following script to repair the errror")
        print("/home/pi/dos/halpha/sun_catching/upload_image.py")
        return
        
