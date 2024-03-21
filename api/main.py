from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
import subprocess
import uvicorn
import logging
import secrets





app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")

# HTTPBasic instance for basic authentication
security = HTTPBasic()

# Replace 'your_username' and 'your_password' with the desired credentials
USERNAME = "pi"
PASSWORD = "halpha"

target_script = 'livestream.py'
target_script_path = "/home/pi/docs/halpha/sun_catching/livestream.py"
venv_activate_script = "/home/pi/docs/halpha/venv/bin/activate"

def is_script_running(script_name):
    command = f"ps aux | grep '{script_name}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout.strip()
    word1 = "python"
    if word1 in output:
        return True
    else:
        return False
     
def execute_script():
    command = f"bash -c 'source {venv_activate_script} && python {target_script_path}'"
    subprocess.run(command, shell=True, text=True)
    
def stop_script():
    try:
        command1 = ["pkill", "-f", "python /home/pi/docs/halpha/sun_catching/livestream.py"]
        subprocess.run(command1, shell=False, text=True)
        command2 = ["pkill", "-f", "python livestream.py"]
        subprocess.run(command2, shell=False, text=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error stopping script: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), request: Request = None):
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        print("help")
        return False
    return True



@app.get("/execute_script", response_class=HTMLResponse)
def trigger_script_execution(request: Request, authorized: bool = Depends(authenticate_user)):
    if authorized == True:
        execute_script()
        #return RedirectResponse(url="/")
    else:
        print("not authorized")
        return RedirectResponse(url="/")
    
@app.get("/stop_script", response_class=HTMLResponse, dependencies=[Depends(authenticate_user)])
def trigger_script_stop(request: Request):
    stop_script()
    return RedirectResponse(url="/")

@app.get("/get_status", response_class=JSONResponse)
def get_script_status():
    print(is_script_running(target_script))
    script_status = "Running" if is_script_running(target_script) else "Not Running"
    return {"status": script_status}

@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    return f"""
    <html>
        <head>
            <title>Halpha Livestream</title>
            <script>
                // Function to update the script status on the webpage
                function updateStatus(newStatus) {{
                    document.getElementById("scriptStatus").innerText = "Script Status: " + newStatus;
                }}

                // Function to periodically fetch the script status from the server
                async function pollStatus() {{
                    while (true) {{
                        try {{
                            // Fetch the status from the server
                            const response = await fetch("/get_status");
                            const data = await response.json();
                            // Update the status on the webpage
                            updateStatus(data.status);
                        }} catch (error) {{
                            console.error("Error fetching script status:", error);
                        }}
                        // Wait for 5 seconds before polling again
                        await new Promise(resolve => setTimeout(resolve, 5000));
                    }}
                }}

                // Start polling for the script status when the page loads
                window.onload = async function() {{
                    // Fetch the initial status before starting the polling
                    try {{
                        const initialResponse = await fetch("/get_status");
                        const initialData = await initialResponse.json();
                        console.log("Initial status response:", initialData);  // Log the response
                        updateStatus(initialData.status);
                    }} catch (error) {{
                        console.error("Error fetching initial script status:", error);
                    }}

                    // Start polling for script status
                    pollStatus();
                }};
            </script>
        </head>
        <body>
            <h1>Halpha livestream PMOD/WRC Davos</h1>
            <p>Click the link below to trigger the script:</p>
            <a href="{request.url_for("trigger_script_execution")}">Start Livestream</a>
            <p>Click the link below to stop the script:</p>
            <a href="{request.url_for("trigger_script_stop")}">Stop Livestream</a>
            <p id="scriptStatus">Livestream Status: Loading...</p>
            <h2>Latest Image</h2>
            <img src="/images/sun2.png" alt="Latest Image" width="960" height="540">
        </body>
    </html>
    """
if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn, listen on all available network interfaces
    uvicorn.run(app, host="0.0.0.0", port=8000)



#http://172.16.8.52:8000/  to connect via a device in the network (works only when the main.py script is running on the raspi)
