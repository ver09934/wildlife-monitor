# Wildlife Monitor
Detect the presence of wildlife and present the data with a web frontend.

## Connections
### PIR Sensor
### Barometric Pressure/Altitude/Temperature Sensor
### Camera
### LED
Optionally, an led can be attached to BCM 4 and ground in series with a 100 ohm resistor. Currently, this LED would indicate when motion is detected and the camera is recording.

## HTTP Server Setup
An HTTP server such as [apache2](https://httpd.apache.org/) should be configured to run php, and have it's document root configured to be the `/site` directory of this repository. Then, the data directory, which stores videos and metadata, should been created, either manually or by running `backend/sensors.py`. Once created (the default location is for the data directory /data, which is gitignored), this directory should be symlinked to `/site/data` (which is also gitignored) to make it accessible to the HTTP server. This can be achieved by running something like the following:
```
$ ln -s ../data site/data
```
(The paths are relative to the location of the symbolic link - without the `../`, we would end up with a broken link that links to itself).

## Running
(This will be updated once there is something to run).

## Notes
To prevent `.pyc` files or `__pycache__` directories from being created, run python with the `-B` option.
