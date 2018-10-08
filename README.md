# Wildlife Monitor
This project is designed to detect the presence of wildlife and record video footage and data of the events. Each camera unit pushes the footage and data to a server, which displays the aggregated data in a user-friendly web frontend. The individual units are based on the Raspberry Pi 3 Model B+ with the Camera Module V2, though it could likely be made to work on other versions without much trouble.

## Connections
Below are instructions on how to connect the various sensors to the Raspberry Pi. Helpful references for the pinout can be found at [pinout.xyz](https://pinout.xyz/), with a quick search online, or embedded below.

![link](https://www.raspberrypi-spy.co.uk/wp-content/uploads/2014/07/Raspberry-Pi-GPIO-Layout-Model-B-Plus-rotated.png)

### PIR Sensor
The units use the the HC-SR501 PIR Motion Sensor, which is readily available at a number of online retailers. This should be connected as follows:
* VCC of the PIR sensor goes to +5V on the Pi (such as physical pin 4)
* GND of the PIR sensor goes to Ground on the pi (such as physical pin 6)
* The signal out pin of the PIR sensor goes to BCM 17 on the Pi (physical pin 11)

In at least the limited batch of sensors we tested, we found that some modifications were neccesary in order to achieve optimal performance from the sensors. The main sources of false triggers seemed to be RF interference caused by the Pi's communication on WiFi frequencies, which would cause interference on the sensor's power lines, and random ambient IR level fluctuations. For the first issue, several fixes were neccesary:
* solder a 10K resistor between the signal pin of the PIR sensor and ground (this can be soldered directly to the pins underneath the plastic fresnel lens)
* solder a 220 nF between pins 12 and 13 of the BISS0001 chip on the PIR sensor board (a schematic of the PIR can be found [here](https://www.mpja.com/download/31227sc.pdf))
* Wrap the power and ground wires going to the sensor around an appropriately sized ferrite ring
* Shield the sensor from the rest of the circuitry using aluminum foil (this may not be neccesary, or even that important)

For the second issue, we found it helpful to simply restrict the focal width of the sensor, originally by placing it in the end of a cardboard tube. In a future design iteration, this feature will be build into the 3D-printed case.

### Barometric Pressure/Altitude/Temperature Sensor
The units use the MPL3115A2 I2C Barometric Pressure/Altitude/Temperature Sensor, available [here](https://www.adafruit.com/product/1893). This should be connected as follows:
* Vin on the Baro goes to +3.3V (such as physical pin 1)
* GND on the Baro goes to Ground on the Pi (such as physical pin 14)
* SCL on the Baro goes to BCM 3 (SCL) on the Pi (physical pin 5)
* SDA on the Baro goes to BCM 2 (SDA) on the Pi (physical pin 3)

### Camera
The camera is connected as shown in the Raspberry Pi documentation [here](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/4), with the ribbon cable being connected to the camera connector on the board.

### LED
Optionally, an led can be attached to BCM 4 (physical pin 7) and a ground pin (such as physical pin 9) in series with a 100 ohm resistor. (BCM 4 has a ground pin directly below it). In the curent code, this LED indicates when motion is detected and the camera is recording.

## Webserver Setup
An http server such as [apache2](https://httpd.apache.org/) should be configured to use the modules `php` and `php-xml`, and it have its document root set to be the `frontend` directory of this repository.

In addition, the gitignored directory `frontend/data` should be created. This is the directory in which all the individual Pis will send their data, and as such it should have permissions set such that the user(s) being used by the client Pis to connect to the server can read and write to it.

## Unit Setup

### OS Installation and Setup
To set up the unit, flash the SD card with raspbian, ideally the headless version, which uses fewer system resources. In addition, you should configure a wireless internet connection by editing the file `/etc/wpa_supplicant/wpa_supplicant.conf`, and insure that you have ssh access to the Pi. More information can be found [here](https://www.raspberrypi.org/documentation/configuration/wireless/).

### SSH Keys
Each Pi must be configured to use ssh keys to connect to the server. To do this, run `$ ssh-keygen`, or `$ ssh keygen -b 4096` for a 4096-bit key. Be sure not to set a passphrase, as this would prevent the script from being able to automate the process of synchronizing data with the server. They key can be copied to the server by running `$ ssh-copy-id user@hostname`, with your user information for the remote server.

In addition, one should manually ssh into the server after configuring ssh keys to insure that the server is in the list of known hosts, and that a connection can be made with no user confirmation, so that the script will be able to connect automatically.

For more information on setting up ssh keys, see [here](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-on-ubuntu-1804).

### Script Download and Dependencies
The repository can be cloned anywhere on the Pi, such as in the user's home directory. As long as you are running a recent version of Raspbian, the dependencies can all be installed with `apt` and `pip`:
```bash
$ sudo apt install $(cat apt-reqs.txt)
$ sudo pip install -r requirements.txt
```
(The apt requirements should be installed first, since they insure that pip is installed.)

If you would prefer to install the pip requirements in a virtual environment, one can be created by running the following commands in the python script directory before installing the pip requirements:
```bash
$ python3 -m venv venv
$ . venv/bin/activate
```

### info.xml
Currently, a file called `info.xml` is used to configure some parameters used by the sensor script, so that it is not neccesary to modify the script file. It is gitignored, so you must create it yourself in the root directory of the repository.

It is important to note that the `name` fields of separate units must be unique, so it is a good idea to use a naming scheme that will not result in conflicting names, and you must insure that no other units of the same name are attempting to send data to the same server.

An example configuration is shown below:
```xml
<?xml version="1.0"?>
<info>
    <name>testunit1</name>
    <prettyname>Test Unit</prettyname>
    <serveruser>exampleuser</serveruser>
    <serverdomain>subdomain.exampledomain.com</serverdomain>
    <serverdatadir>/var/www/html/wildlife-monitor/frontend/data/</serverdatadir>
</info>

```

### Case and Mounting
A 3D printed case is being designed, and is still a work in progress.

## Running
The server simply needs to serve the frontend files and listen for incoming ssh connections.

To run the sensor script on the Pi, navigate to the backend directory of this repository, and run the script, perhaps in a `tmux` session, with `$ python3 sensors-threaded.py`. To prevent `.pyc` files or `__pycache__` directories from being created, run python with the `-B` flag.
