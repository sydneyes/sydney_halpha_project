import subprocess

def run_smbclient():
    command = [
        "/usr/bin/smbclient",
        "//ad.pmodwrc.ch/Institute",
        "--user=web.service@ad.pmodwrc.ch%SCRLvugFhi0dKu7K5XnF",
        "--workgroup=AD.pmodwrc.ch",
        "--command", "cd Infrastructure/WWW/www.pmodwrc.ch/htdocs/images/halpha; put sun.PNG"
    ]

    try:
        subprocess.run(command, check=True)
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        
run_smbclient()