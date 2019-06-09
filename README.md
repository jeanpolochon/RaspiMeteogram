# RaspiMeteogram
Meteogram for Raspberry Pi based on Highcharts.

## Hardware
* Raspberry Pi (or Beaglebone Black but I haven't tried)
* X_NUCLEO_IKS01A1 (X_NUCLEO_IKS01A2 is also a viable option but cf Issue #4)
* 4 Male to Female jumper cables

## Hardware setup
1. Connect the GND, 3.3V, SDA, SCL pins of the Raspberry Pi to the ones of the sensor board
2. Install Raspbian Lite (or Raspbian) on an SD card and power the Raspberry Pi

## Software setup
A step by step workflow is also describe in the [wiki](https://github.com/jeanpolochon/RaspiMeteogram/wiki).
1. Clone the repository on the home directory of the Raspberry pi
```
    cd ~
    git clone git@github.com:jeanpolochon/RaspiMeteogram.git
```
2. Run the installation script (it might take a while).
```
    cd RaspiMeteogram
    sudo ./install.sh
```
You can check the log file located in ./log/log_install.txt
3. The server should be up and running
You can check the log file located in /var/log/meteogram.log
