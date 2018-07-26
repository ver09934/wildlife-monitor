# Wildlife Monitor
This project is designed to detect the presence of wildlife and record video footage and data of the events. Each camera unit pushes the footage and data to a sever, which displays the aggregated data in a user-friendly web frontend. The individual units are based on the Raspberry Pi 3 Model B+ with the Camera Module V2, though it could likely be made to work on other versions without much trouble.

## Connections
### PIR Sensor
The units use the the HC-SR501 PIR Motion Sensor, which is readily available at a number of online retailers. This should be connected as follows:
* TODO

<!--
Eventually, the camera may have a part in the motion detection as well...
-->

### Barometric Pressure/Altitude/Temperature Sensor
The units use the MPL3115A2 I2C Barometric Pressure/Altitude/Temperature Sensor, available [here](https://www.adafruit.com/product/1893). This should be connected as follows:
* (TODO)

### Camera
The camera is connected as shown in the Raspberry Pi documentation [here](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/4).

### LED
Optionally, an led can be attached to BCM 4 and ground in series with a 100 ohm resistor. In the curent code, this LED indicates when motion is detected and the camera is recording.

<!--
## Central Webserver Setup
-->

<!--
## Setup / Running
(This will be updated once there is something to run).
-->

## Notes
To prevent `.pyc` files or `__pycache__` directories from being created, run python with the `-B` option.

<!--
This should be noted if a dockerized version is ever created.
-->

