from fastapi import FastAPI, Request, HTTPException, Depends, status, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
import subprocess
import uvicorn
import logging
import psutil


app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")

# HTTPBasic instance for basic authentication
security = HTTPBasic()

# Replace 'your_username' and 'your_password' with the desired credentials
USERNAME = "pi"
PASSWORD = "halpha"

target_script = 'solar_cam'
target_script_path = "/home/pi/docs/sydney_halpha_project/sun_catching_in_cpp/solar_cam"

SCRIPT_OPTIONS = {
    "standard": {
        "name": "solar_cam",
        "path": "/home/pi/docs/sydney_halpha_project/sun_catching_in_cpp/solar_cam",
        "dir": "/home/pi/docs/sydney_halpha_project/sun_catching_in_cpp"
    },
    "optimized": {
        "name": "solar_cam",
        "path": "/home/pi/docs/sydney_halpha_project/sun_catching_in_cpp_optimized/solar_cam",
        "dir": "/home/pi/docs/sydney_halpha_project/sun_catching_in_cpp_optimized"
    }
}

current_script = None
current_args = []

    
def is_script_running(script_path):
    command = f"pgrep -f '^{script_path}$'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def stop_script():
    global current_script
    if not current_script:
        logging.info("No script currently tracked.")
        return
    try:
        result = subprocess.run(["pkill", "-f", current_script], capture_output=True, text=True)
        if result.returncode != 0:
            logging.warning(f"pkill failed: {result.stderr}")
            # Fallback: Find the process ID manually and kill it
            pid_result = subprocess.run(["pgrep", "-f", current_script], capture_output=True, text=True)
            if pid_result.returncode == 0:
                pids = pid_result.stdout.strip().split("\n")
                for pid in pids:
                    subprocess.run(["kill", "-9", pid])
            else:
                logging.error(f"Failed to find process: {pid_result.stderr}")
    except Exception as e:
        logging.error(f"Error stopping script: {e}")


def execute_script(script_key, args):
    global current_script, current_args
    script_info = SCRIPT_OPTIONS.get(script_key)

    if not script_info:
        logging.error("Invalid script key.")
        return
    
     # Stop previous if running
    stop_script() 

    # Compile if not already built
    try:
        subprocess.run(["make"], cwd=script_info["dir"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Build failed: {e}")
        return

    # Start new
    try:
        current_script = script_info["path"]
        current_args = args
        subprocess.Popen([current_script] + args)
        logging.info(f"Started {current_script} with args {args}")
    except Exception as e:
        logging.error(f"Error starting script: {e}")


#simple login, if password is wrong, you probably need to open another tab
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), request: Request = None):
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

@app.post("/start", response_class=RedirectResponse)
async def handle_start_script(
    request: Request,
    authorized: bool = Depends(authenticate_user),
    script_type: str = Form(...),
    threads: int = Form(...),
    exposure: int = Form(...),
    nimages: int = Form(...)
):
    if authorized == True:
        args = [
            f"--threads={threads}",
            f"--exposure={exposure}",
            f"--nimages={nimages}"
        ]
        execute_script(script_type, args)
        return RedirectResponse(url="/", status_code=303)
    else:
        print("not authorized")
        return RedirectResponse(url="/")
    


@app.get("/stop_script", response_class=JSONResponse, dependencies=[Depends(authenticate_user)])
def trigger_script_stop(request: Request):
    stop_script()
    script_status = "Running" if is_script_running(target_script_path) else "Not Running"
    return {"status": script_status}

@app.get("/get_status", response_class=JSONResponse)
def get_script_status():
    print(is_script_running(target_script))
    script_status = "Running" if is_script_running(target_script_path) else "Not Running"
    return {"status": script_status}

@app.get("/cpu", response_class=JSONResponse)
def get_cpu_usage():
    return {"cpu_percent": psutil.cpu_percent(interval=None)}

@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    return f"""
    <html>
        <head>
            <title>Halpha Livestream</title>
            <script>
                let refreshInterval = 5000;
                let imageIntervalId = null;

                function updateStatus(newStatus) {{
                    document.getElementById("scriptStatus").innerText = "Script Status: " + newStatus;
                }}

                async function pollScriptStatus() {{
                    let lastStatus = null;
                    while (true) {{
                        try {{
                            const response = await fetch("/get_status");
                            const data = await response.json();
                            if (data.status !== lastStatus) {{
                                updateStatus(data.status);
                                lastStatus = data.status;
                            }}
                        }} catch (error) {{
                            console.error("Error fetching script status:", error);
                        }}
                        await new Promise(resolve => setTimeout(resolve, 5000));
                    }}
                }}

                async function pollCpuUsage() {{
                    while (true) {{
                        try {{
                            const response = await fetch("/cpu");
                            const data = await response.json();
                            document.getElementById("cpuStatus").innerText = "CPU Usage: " + data.cpu_percent + "%";
                        }} catch (error) {{
                            console.error("Error fetching CPU usage:", error);
                        }}
                        await new Promise(resolve => setTimeout(resolve, 5000));
                    }}
                }}

                async function stopLivestream() {{
                    try {{
                        const response = await fetch("/stop_script");
                        const data = await response.json();
                        updateStatus(data.status);
                    }} catch (error) {{
                        console.error("Error stopping the script:", error);
                    }}
                }}

                function startImageRefresh() {{
                    if (imageIntervalId) {{
                        clearInterval(imageIntervalId);
                    }}
                    imageIntervalId = setInterval(() => {{
                        const img = document.getElementById("liveImage");
                        img.src = `/images/sun.PNG?timestamp=${{Date.now()}}`;
                    }}, refreshInterval);
                }}

                window.onload = function () {{
                    // Initialize refresh interval input
                    const input = document.getElementById("refreshIntervalInput");
                    input.value = refreshInterval;
                    input.addEventListener("change", () => {{
                        const newValue = parseInt(input.value);
                        if (!isNaN(newValue) && newValue > 0) {{
                            refreshInterval = newValue;
                            startImageRefresh();
                        }}
                    }});

                    // Kick off all polling
                    pollScriptStatus();
                    pollCpuUsage();
                    startImageRefresh();

                    // Load initial status
                    fetch("/get_status")
                        .then(response => response.json())
                        .then(data => updateStatus(data.status))
                        .catch(error => console.error("Error fetching initial script status:", error));
                }};
            </script>
        </head>
        <body>
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h1>Halpha Livestream PMOD/WRC Davos</h1>
                    <h2>Start Livestream</h2>
                    <form action="/start" method="post" style="margin-top: 20px;">
                        <label style="display: inline-block; width: 150px;">Script Version:</label>
                        <select name="script_type" style="width: 150px;">
                            <option value="standard">Standard</option>
                            <option value="optimized">Optimized</option>
                        </select>
                        <br>

                        <label style="display: inline-block; width: 150px;">Threads:</label>
                        <input type="number" name="threads" value="3" required style="width: 100px;">
                        <br>

                        <label style="display: inline-block; width: 150px;">Exposure:</label>
                        <input type="number" name="exposure" value="500" required style="width: 100px;">
                        <br>

                        <label style="display: inline-block; width: 150px;">nimages:</label>
                        <input type="number" name="nimages" value="10" required style="width: 100px;">
                        <br>

                        <button type="submit" style="margin-top: 10px;">Start Script</button>
                    </form>

                    <h2>Stop Livestream</h2>
                    <button onclick="stopLivestream()">Stop Script</button>

                    <p id="scriptStatus">Script Status: Loading...</p>
                    <p id="cpuStatus">CPU Usage: Loading...</p>

                    <h3>Set Image Refresh Interval (ms):</h3>
                    <input type="number" id="refreshIntervalInput" min="100">
                </div>

                <div>
                    <h2>Latest Image</h2>
                    <img id="liveImage" src="/images/sun.PNG" alt="Latest Image" width="480" height="270" style="float: right;">
                </div>
            </div>
        </body>
    </html>
    """


if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn, listen on all available network interfaces
    uvicorn.run(app, host="0.0.0.0", port=8000)



#http://172.16.8.52:8000/  to connect via a device in the network (works only when the main.py script is running on the raspi)
#ip's change sometimes(maybe someone could configure a static ip) currently, the ip is 172.16.10.248
#you can check the ip of the pi with an nmap scan (download nmap, type nmap -sn 172.16.0.0/12 in cmd)
#or type in the pi console: hostname -I