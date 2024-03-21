# Remote Access - API

The idea of this script is to provide an API whic is accessible for all computers on the local network with which the RaspberryPi is connected. It works in a similar way to the [GUI](https://pmodwrc.github.io/halpha/reference/gui/) and also displays the status of the livestream and has the function to start and stop the livestream. Furthermore the latest image is displayed on the main side.

## Code Description

The API is made with the [FastAPI library](https://fastapi.tiangolo.com/reference/openapi/docs/) and the livesream is controlled with the [Subprocess library](https://docs.python.org/3/library/subprocess.html) which is able to execute commands in the shell. In our case starting and stopping the livestream and asking for the status. For this functions we use the same commands as for the [GUI](https://pmodwrc.github.io/halpha/reference/gui/). 

### API Management
First of all the app is initialised an afterwards there is one mainsite that has different URL's to call the start and stop function. When one of this URL's gets called by clicking on it the user gets asked for username and password. This happens with the Depends function from FastAPI:

```python

@app.get("/stop_script", response_class=HTMLResponse, dependencies=[Depends(authenticate_user)])

```

This code calls the authenticate_user function and checks wheter the given credentials are right or wrong and executes afterwards the desired command with `suprocess.run`.

To display the image the directory of the image is mounted and afterwards the specific image is called in the HTML part of the mainsite.

```python
app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")

``` 
In the HTML part the size and the position of the image is determined. To make sure the image gets updated every time the website reloads a timestamp is given to the image for the website.

```html
<img src="/images/sun2.png" alt="Latest Image" width="960" height="540">
```

## Usage
To use this API in the local network the belonging Python [script](https://github.com/pmodwrc/halpha/blob/main/api/main.py) must be running on the RaspberryPi. The API is run via the Uvicorn library.The following libraries have to be installed with pip to run the API:

- FastAPI
- Subprocess
- Uvicorn

The API should be accessible on the folowing link if you are connected to the same network as the RaspberryPi is running in.

```
http://<RaspberryPi IP adress>:8000/
```


## Python Script
The script can be found [here](https://github.com/pmodwrc/halpha/blob/main/api/main.py).