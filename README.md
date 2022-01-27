# Brewmoth
Project to control a peltier driven fermentation chamber for home brewing

# Fresh setup

1. Install the following:
```shell
sudo apt update;
sudo apt install python3 python3-pip nginx libatlas-base-dev libopenjp2-7 pigpio
sudo apt update
sudo apt install libatlas-base-dev
sudo pip3 install virtualenv
sudo systemctl enable pigpiod
```
2. Copy repository to `/brewmoth`
3. Create a virtual environment with following requirements
```shell
cd /brewmoth
virtualenv brewvenv
source brewvenv/bin/activate
pip3 install uwsgi flask flask_cors systemd requests numpy scipy matplotlib pigpio gpiozero
deactivate
```
3. `ls /sys/bus/w1/devices/` to get the serial numbers of any installed 1-wire type temperature sensors. 
These will be a long string starting with some numbers, not anything that starts with `w1`  
4. Copy `example-config.json` and set the properties like so:
   1. First, change the name as required.
   2. Second, edit the "Temperature sensors" section so there is at least one sensor of type "Main".
   The serial portion is where you add the string identified with the above command.
   The name of each sensor is completely up to you.
   If you want to have the moth update brewfather, add an entry like this: `"Brewfather": True`
5. `cd /sys/bus/w1/devices/` and list the thermometers
8. If using Nginx, link to configuration file, test the configuration works and restart nginx:
```shell
sudo ln -s /brewmoth/brewmoth_server/brewmoth.nginx /etc/nginx/sites-enabled/brewmoth
sudo nginx -t
sudo service nginx restart
```
If not using nginx, you'll need to set up another service to connect to the unix socket that brewmoth is listening on.

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

To do so, stop any running brewmoth instance that you may have started through the command-line,
and then activate the service file:
```shell
ln -s /etc/systemd/system/brewmoth.service /brewmoth/brewmoth_server/brewmoth.service`
sudo systemctl daemon-reload
sudo service enable brewmoth
sudo service brewmoth restart
````

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

### Access command from anywhere

You can add the brewmoth directory to PATH To allow the above commands to be called from anywhere.
1. Call `sudo nano ~/.profile` to start editing the `.profile` file
2. Add the following line `PATH=~/opt/bin:$PATH` to the end of the file.
3. Exit with `ctrl+x`, select `y` and accept.