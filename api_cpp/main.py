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

SCRIPT_OPTIONS = {
    "set_focus": {
        "name": "set_focus",
        "path": "/home/pi/docs/sydney_halpha_project/sun_catching_in_cpp_optimized/set_focus",  
        "dir": "/home/pi/docs/sydney_halpha_project/sun_catching_in_cpp_optimized"
    },
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

    
#def is_script_running(script_path):
#    command = f"pgrep -f '^{script_path}$'"
#    result = subprocess.run(command, shell=True, capture_output=True, text=True)
#    return result.returncode == 0

def is_script_running(script_path):
    for proc in psutil.process_iter(['cmdline']):
        try:
            if script_path in ' '.join(proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


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
        if (script_key == "standard") or (script_key == "optimized"):
            subprocess.run(["make"], cwd=script_info["dir"], check=True)
        elif (script_key == "set_focus"):
            subprocess.run(["make", "focus"], cwd=script_info["dir"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Build failed: {e}")
        return

    # Start new
    try:
        current_script = script_info["path"]
        current_args = args
        subprocess.Popen([current_script] + args)
        logging.info(f"Started {current_script} with args {args}")
        #time.sleep(2) # used so that script status is polled correctly (can be done more elegantly), need to import time
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
    nimages: int = Form(...),
    refresh: str = Form("200") 
):
    if authorized == True:
        args = []
        if script_type == "optimized":
            args.extend([
                f"--threads={threads}",
                f"--exposure={exposure}",
                f"--nimages={nimages}"
            ])
        elif script_type == "set_focus":
            args.extend([
                f"--exposure={exposure}",
                f"--refresh={refresh}"
            ])
        elif script_type == "standard":
            # No args needed
            pass

        execute_script(script_type, args)
        return RedirectResponse(url=f"/?script_type={script_type}&threads={threads}&exposure={exposure}&nimages={nimages}", status_code=303)
    else:
        print("not authorized")
        return RedirectResponse(url="/")


@app.get("/stop_script", response_class=JSONResponse, dependencies=[Depends(authenticate_user)])
def trigger_script_stop(request: Request):
    stop_script()
    status = "Running" if current_script and is_script_running(current_script) else "Not Running"
    return {"status": status}

@app.get("/get_status", response_class=JSONResponse)
def get_script_status():
    status = "Running" if current_script and is_script_running(current_script) else "Not Running"
    return {"status": status}

@app.get("/cpu", response_class=JSONResponse)
def get_cpu_usage():
    return {"cpu_percent": psutil.cpu_percent(interval=1)}

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

                function getQueryParam(name) {{
                    const urlParams = new URLSearchParams(window.location.search);
                    return urlParams.get(name);
                }}

                function toggleParameterInputs() {{
                    const scriptType = document.querySelector('select[name="script_type"]').value;
                    const threadInput = document.getElementById("threadInput");
                    const exposureInput = document.getElementById("exposureInput");
                    const nimagesInput = document.getElementById("nimagesInput");
                    const refreshInput = document.getElementById("refreshIntervalInput");

                    if (scriptType === "standard") {{
                        threadInput.style.display = "none";
                        exposureInput.style.display = "none";
                        nimagesInput.style.display = "none";
                        refreshInput.parentElement.style.display = "block";
                    }} else if (scriptType === "optimized") {{
                        threadInput.style.display = "block";
                        exposureInput.style.display = "block";
                        nimagesInput.style.display = "block";
                        refreshInput.parentElement.style.display = "block";
                    }} else if (scriptType === "set_focus") {{
                        threadInput.style.display = "none";
                        exposureInput.style.display = "block";
                        nimagesInput.style.display = "none";
                        refreshInput.parentElement.style.display = "block";
                    }}
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
                        const scriptType = getQueryParam("script_type");
                        let imageName = "sun_halpha.png"; // default

                        if (scriptType === "set_focus") {{
                            imageName = "test_focus.png"; // we'll assume TIFF is converted to PNG
                        }}

                        img.src = `/images/${{imageName}}?timestamp=${{Date.now()}}`;
                    }}, refreshInterval);
                }}

                window.onload = function () {{
                    const urlParams = new URLSearchParams(window.location.search);
                    
                    const input = document.getElementById("refreshIntervalInput");
                    const savedInterval = localStorage.getItem("refreshInterval");
                    refreshInterval = savedInterval ? parseInt(savedInterval) : 5000;
                    input.value = refreshInterval;

                    input.addEventListener("change", () => {{
                        const newValue = parseInt(input.value);
                        if (!isNaN(newValue) && newValue > 0) {{
                            refreshInterval = newValue;
                            localStorage.setItem("refreshInterval", refreshInterval);
                            startImageRefresh();
                        }}
                    }});

                    document.querySelector('select[name="script_type"]').addEventListener("change", toggleParameterInputs);
                    toggleParameterInputs();

                    document.querySelector("form").addEventListener("submit", () => {{
                        const refreshValue = document.getElementById("refreshIntervalInput").value || "200";
                        document.getElementById("refreshHiddenInput").value = refreshValue;
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
                <div style="flex: 1; margin-right: 20px;">
                    <h1>Halpha Livestream PMOD/WRC Davos</h1>
                    <h2>Start Livestream</h2>
                    <form action="/start" method="post" style="margin-top: 20px;">
                        <label style="display: inline-block; width: 150px;">Script Version:</label>
                        <select name="script_type" style="width: 150px;">
                            <option value="set_focus">Set Focus</option>
                            <option value="standard">Standard</option>
                            <option value="optimized">Optimized</option>
                        </select>
                        <br>
                        <div id="threadInput">
                            <label style="display: inline-block; width: 150px;">Worker threads:</label>
                            <input type="number" name="threads" value="3" style="width: 100px;">
                            <br>
                        </div>
                        <div id="exposureInput">
                            <label style="display: inline-block; width: 150px;">Exposure:</label>
                            <input type="number" name="exposure" value="400" style="width: 100px;">
                            <br>
                        </div>
                        <div id="nimagesInput">
                            <label style="display: inline-block; width: 150px;">nimages:</label>
                            <input type="number" name="nimages" value="10" style="width: 100px;">
                            <br>
                        </div>

                        <input type="hidden" name="refresh" id="refreshHiddenInput">
                        <button type="submit" style="margin-top: 10px;">Start Script</button>
                    </form>
                    <h2>Stop Livestream</h2>
                    <button onclick="stopLivestream()">Stop Script</button>

                    <p id="scriptStatus">Script Status: Loading...</p>

                    <h3>Set Image Refresh Interval (ms):</h3>
                    <input type="number" id="refreshIntervalInput" min="100">
                    <p id="cpuStatus">CPU Usage: Loading...</p>
                </div>

                <div style="flex: 1; text-align: center; margin-left: -400px;">
                    <h2>Latest Image</h2>
                    <img id="liveImage" src="/images/sun_halpha.png" alt="Latest Image" width="960" height="540"> 
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