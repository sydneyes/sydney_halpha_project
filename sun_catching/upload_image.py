import subprocess
import os


user = os.getenv("SAMBA_USER", "<your_user>")
password = os.getenv("SAMBA_PASSWORD", "<your_password>")
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
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        
run_smbclient()