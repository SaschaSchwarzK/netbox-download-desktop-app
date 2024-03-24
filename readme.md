# Netbox Data Downloader

This desktop application is developed in Python and provides the ability to download the device, virtual-device-context and virtual-machine data from a netbox server via the REST API and save the data to disk as CSV/TSV file.

## Installation

### Windows
Install the latest version of Python from Microsoft Store

Check the version of Python in a cmd window
`python3 --version`

Install virtualenv
`python3 -m pip install virtualenv`

Cd to the directory where you cloned your this repository
`cd path/to/netbox_app`

Create a new virtual environment
`python3 -m venv C:\path\to\the\repository\netbox_app\venv`

Activate the virtualenv
`C:\path\to\the\repository\netbox_app\venv\Scripts\activate`

Your prompt should have changed to something like this
`(venv) C:\Users\....`

Install the dependencies from the requirements file
`python3 -m pip install -r requirements.txt`

Run the application
`python3 app.py`

### Macintosh
Install the python with the method of your choice. The version that comes with Mac OS is often outdated.

Check the version of Python in a cmd window
`python3 --version`

Install virtualenv
`python3 -m pip install virtualenv`

Cd to the directory where you cloned your this repository
`cd path/to/netbox_app`

Create a new virtual environment
`virtualenv venv`

Activate the virtualenv
`source venv/bin/activate`

Your prompt should have changed to something like this
`(venv) /....`

Install the dependencies from the requirements file
`python3 -m pip install -r requirements.txt`

Run the application
`python3 app.py`

## Tipps and Hints

When the application is busy it might appear as "not responding" on Windows. On Mac you should see a busy animation of the mouse pointer.
Just wait for the operation to complete.

## Known Issues
The site and region filter are currently not working for virtual-device-context. The reason is that netbox has not implement this as filter in the REST API. It would require to follow the relationship from the device to get the site and the region via the site.


