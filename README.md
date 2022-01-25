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
3. Create a virtual environment with uwsgi
```shell
cd /brewmoth
virtualenv brewvenv
source brewvenv/bin/activate
pip3 install uwsgi flask flask_cors systemd requests numpy scipy matplotlib pigpio gpiozero
deactivate
```
4. Edit `config.json` and set the name
5. `cd /sys/bus/w1/devices/` and list the thermometers
6. Edit `/brewmoth/hardware_control/temperature_sensors.py` and set the thermometer
7. Activate the service file:
```shell
ln -s /etc/systemd/system/brewmoth.service /brewmoth/brewmoth_server/brewmoth.service`
sudo systemctl daemon-reload
sudo service enable brewmoth
sudo service brewmoth restart
````
8. Create Nginx configuration file:
```shell
sudo nano /etc/nginx/sites-available/brewmoth
```
9. And copy the following:
```shell
server {
    listen 555;
    server_name 127.0.0.1;
    
    location / {
        include         uwsgi_params;
        uwsgi_pass      unix:/brewmoth/brewmoth.sock;
    }
}
```
10. Enable the site:
```shell
sudo ln -s /etc/nginx/sites-available/brewmoth /etc/nginx/sites-enabled/brewmoth
```
11. Test file and restart nginx:
```shell
sudo nginx -t
sudo service nginx restart
```

You can now connect and use the following commands from the brewmoth directory:
`./temps`
`./fans`
`./peltiers`