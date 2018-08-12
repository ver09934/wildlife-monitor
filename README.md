# Wildlife Monitor
This project is designed to detect the presence of wildlife and record video footage and data of the events. Each camera unit pushes the footage and data to a sever, which displays the aggregated data in a user-friendly web frontend. The individual units are based on the Raspberry Pi 3 Model B+ with the Camera Module V2, though it could likely be made to work on other versions without much trouble.

## Connections
Below are instructions on how to connect the various sensors to the Raspberry Pi. Helpful reference fors the pinout can be found at [pinout.xyz](https://pinout.xyz/), with a quick search online, or embedded below.

![link](https://www.raspberrypi-spy.co.uk/wp-content/uploads/2014/07/Raspberry-Pi-GPIO-Layout-Model-B-Plus-rotated.png)

### PIR Sensor
The units use the the HC-SR501 PIR Motion Sensor, which is readily available at a number of online retailers. This should be connected as follows:
* VCC of the PIR sensor goes to +5V on the Pi (such as physical pin 4)
* GND of the PIR sensor goes to Ground on the pi (such as physical pin 6)
* The signal out pin of the PIR sensor goes to BCM 17 on the Pi (physical pin 11)
In addition, to significantly reduce the amount of false triggers due to RF interference caused by the Pi's communication on WiFi frequencies, it is helpful to attach a 10K resistor between the signal pin of the PIR sensor and ground.

### Barometric Pressure/Altitude/Temperature Sensor
The units use the MPL3115A2 I2C Barometric Pressure/Altitude/Temperature Sensor, available [here](https://www.adafruit.com/product/1893). This should be connected as follows:
* Vin on the Baro goes to +3.3V (such as physical pin 1)
* GND on the Baro goes to Ground on the Pi (such as physical pin 14)
* SCL on the Baro goes to BCM 3 (SCL) on the Pi (physical pin 5)
* SDA on the Baro goes to BCM 2 (SDA) on the Pi (physical pin 3)

### Camera
The camera is connected as shown in the Raspberry Pi documentation [here](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/4), with the ribbon cable being connected to the camera connector on the board.

### LED
Optionally, an led can be attached to BCM 4 and a ground pin (such as physical pin 9) in series with a 100 ohm resistor. (BCM 4 has a ground pin directly below it). In the curent code, this LED indicates when motion is detected and the camera is recording.

<!--
## Central Webserver Setup

(After server setup)

Create the gitignored directory new-frontend/data, which is where all the individual Pis will send their data to. In addition, insure that this directory is owned by the user that the client Pis will be using to login to the server to sync their data with it.

Dockerimage / Setup / Dependencies / Clone / XML List

## Setup
Several files must be created (xml giving pi codename, YT key)
(TODO: Put key in XML file with name?)

## Running
Currently, to run the script on the Pi end, clone this repository to the Pi, install the dependencies (TODO)
, navigate to the backend directory, and run the script, perhaps in a tmux session, with `$ python3 -B sensors-threaded.py`.

The '-B' should be noted if a dockerized version is ever created.
-->

## Notes
To prevent `.pyc` files or `__pycache__` directories from being created, run python with the `-B` option.
