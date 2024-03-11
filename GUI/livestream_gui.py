from tkinter import messagebox
import tkinter as tk
import paramiko
import os


# Check if the lock file exists
lock_file_path = "gui_lock.lock"

if os.path.isfile(lock_file_path):
    messagebox.showinfo("Error", "Another instance of the GUI is already running.")
    exit()

# Create the lock file
with open(lock_file_path, 'w') as lock_file:
    lock_file.write("")

# Your existing code...

def on_window_close():
    # Remove the lock file when the GUI is closed
    os.remove(lock_file_path)
    # Ask a question in a separate confirmation window
    result = messagebox.askyesno("Closing livestream", "When you close this window you will shut down the livestream")
    if result:
        window.destroy()  # Close the main window if the user confirms
        execute_stop_on_pi(ssh)
        with sftp.file("/home/pi/docs/halpha/sun_catching/error_log.txt", 'w') as file:
            file.write("")

def check_livestream_status(ssh, script_name):
    command = f"ps aux | grep {script_name}"
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode("utf-8")
    return "python" in output

def execute_start_on_pi(ssh):
    command = "source /home/pi/docs/halpha/venv/bin/activate && python /home/pi/docs/halpha/sun_catching/livestream.py"
    ssh.exec_command(command)

def execute_stop_on_pi(ssh):
    ssh.exec_command(f"pkill -f 'python /home/pi/docs/halpha/sun_catching/livestream.py'")
def check_status():
    with sftp.file("/home/pi/docs/halpha/sun_catching/error_log.txt", 'r') as file:
        file_contents = file.read()
    error_status.config(text = file_contents)
    
    state = check_livestream_status(ssh, script_name)
    
    if state == True:
        status = "Status: Livestream is running"
        show_button2()
    else:
        status = "Status: Livestream is not running"
        show_button1()
    label_status.config(text=status)


    window.after(1000, check_status)

def show_button1():
    button1.grid(row=1, column=0, padx=10, pady=10)
    button2.grid_forget()


def show_button2():
    button2.grid(row=1, column=0, padx=10, pady=10)
    button1.grid_forget()

def function_for_button1():
    state = check_livestream_status(ssh, script_name)
    if not state:
        execute_start_on_pi(ssh)

def function_for_button2():
    state = check_livestream_status(ssh, script_name)
    if state:
        execute_stop_on_pi(ssh)
        with sftp.file("/home/pi/docs/halpha/sun_catching/error_log.txt", 'w') as file:
            file.write("")

# Raspberry Pi details
raspberry_pi_ip = "172.16.8.52"
raspberry_pi_username = "pi"
raspberry_pi_password = "raspberry"
port = 22
script_name = "livestream.py"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(raspberry_pi_ip, port, raspberry_pi_username, raspberry_pi_password)
sftp = ssh.open_sftp()
with sftp.file("/home/pi/docs/halpha/sun_catching/error_log.txt", 'w') as file:
    file.write("")

    
# Create the main window
window = tk.Tk()
window.title("Halpha livestream interface")

window.geometry("400x300")

label_status = tk.Label(window, text="Status: Checking...")
label_status.grid(row=0, column=0, padx=10, pady=10)

# Create Button 1
button1 = tk.Button(window, text="Start Livestream", command=function_for_button1)
button1.grid(row=1, column=0, padx=10, pady=10)

# Create Button 2
button2 = tk.Button(window, text="Stop Livestream", command=function_for_button2)
button2.grid(row=1, column=0, padx=10, pady=10)

error_status = tk.Label(window, foreground="red",text="Status: Checking...")
error_status.grid(row=3, column=0, padx=10, pady=10)

# Start the periodic status check
check_status()
window.protocol("WM_DELETE_WINDOW", on_window_close)

with sftp.file("/home/pi/docs/halpha/sun_catching/error_log.txt", 'r') as file:
    file_contents = file.read()
    
# Start the GUI event loop
window.mainloop()

# Close the SSH connection when the GUI is closed
ssh.close()
