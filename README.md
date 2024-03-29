# Brewmoth

## The gist
Brewmoth is a project to convert a Raspberry Pi into a general tool to assist with home-brewing,
but can also be used more generally for temperature logging and control.

## Background
The original motivation was to use create a DYI fermentation chamber using peltier modules,
but the code can be used more generally than that.
For example, you can use it to make a temperature logger that interfaces with brewfather
or to control a standard keezer set-up with InkBird and resistive heater,
but with added temperature logging.

# Fresh setup

## Connecting to the Raspberry pi

This is beyond the scope of this README, but here are some resources.
There are two options:
1. Edit the SD card on your normal computer to add your Wi-Fi details.
   [Here is an example guide on how to do this.](https://forums.raspberrypi.com/viewtopic.php?t=259894])
2. Alternatively you can connect a USB hub with a keyboard and mouse, and an HDMI monitor to add the Wi-Fi details
   as normal

Once the Wi-Fi details can be added you can use `ssh` to connect to the raspberry pi.
[More information can be found here.][1]

## Full installation

1. Create the directory but change `username` to your own username:
   ```shell
   sudo mkdir /brewmoth
   sudo chown username:username /brewmoth
   ```
2. Install the following:
   ```shell
   sudo rpi-update
   sudo apt update
   sudo apt upgrade
   sudo apt install python3 python3-pip nginx libatlas-base-dev libopenjp2-7 pigpio
   sudo apt update
   sudo apt autoremove
   sudo pip3 install virtualenv
   sudo systemctl enable pigpiod
   sudo service pigpiod start
   ```
3. Copy repository to `/brewmoth`
4. Create a virtual environment with following requirements
   ```shell
   cd /brewmoth
   virtualenv brewvenv
   source /brewmoth/brewvenv/bin/activate
   pip3 install uwsgi flask flask_cors systemd requests pigpio gpiozero matplotlib
   deactivate
   ```
5. Type `ls /sys/bus/w1/devices/` to get the serial numbers of any installed 1-wire type temperature sensors. 
   These will be a long string starting with some numbers, not anything that starts with `w1`  
6. Copy `example-config.json` and set the properties like so:
   1. First, change the name as required.
   2. Second, edit the "Temperature sensors" section so there is at least one sensor of type "Main".
   The serial portion is where you add the string identified with the above command.
   The name of each sensor is completely up to you.
   If you want to have the moth update brewfather, add an entry like this: `"Brewfather": True`
7. If using Nginx, link to configuration file, test the configuration works and restart nginx:
   ```shell
   sudo ln -s /brewmoth/brewmoth_server/brewmoth.nginx /etc/nginx/sites-enabled/brewmoth
   sudo nginx -t
   sudo service nginx restart
   ```
   If not using nginx, you'll need to set up another service to connect to the unix socket that brewmoth is listening on.
   
You also can add the brewmoth directory to PATH to allow the above commands to be called from anywhere in the shell
1. Call `sudo nano ~/.profile` to start editing the `.profile` file
2. Add the following line `PATH=~/opt/bin:$PATH` to the end of the file.
3. Exit with `ctrl+x`, select `y` and accept.

## Run from command-line
To troubleshoot, it's best to start brewmoth using the command-line. 
First, you need to turn on the virtual environment:
```
source /brewmoth/brewvenv/bin/activate
```
You can then start the brewmoth using the command:
```commandline
python /brewmoth/wsgi.py
```

## Run as a service

Once you know everything is great, you can configure it the brewmoth service.

### Configure service

To configure it as a service, stop any running brewmoth instance that you may have started through the command-line,
and then activate the service file:
```shell
sudo ln -s /brewmoth/brewmoth_server/brewmoth.service /etc/systemd/system/brewmoth.service
sudo systemctl daemon-reload
sudo systemctl enable brewmoth
sudo service brewmoth restart
````

#### Optional services

If you want to enable temperature control you need to enable the thermostat service:
```shell
sudo ln -s /brewmoth/brewmoth_server/brewmoth-thermostat.service /etc/systemd/system/brewmoth-thermostat.service 
sudo systemctl daemon-reload
sudo systemctl enable brewmoth-thermostat
sudo service brewmoth-thermostat restart
```

### Control service

You can now use normal linux service commands like the ones below:
```shell
sudo service brewmoth stop
sudo service brewmoth start
sudo service brewmoth restart
sudo service brewmoth status
````

### Logs

To see the logs of the brewmoth service do `sudo service brewmoth status` for the latest lines or
`sudo journalctl -u brewmoth.service` for the full history.

## Control Brewmoth

Once brewmoth has been started through the command-line or as a service,
you can use the following commands from the brewmoth directory:
``` commandline
./temps
./track-temps
./fans
./peltiers
```
You can run any of the above commands with `-h` after to get more information on how and why to use them.

Note, for `track-temps` you might need to first activate the virtual environment (see above).

[1]: https://www.raspberrypi.com/documentation/computers/remote-access.html#setting-up-an-ssh-server