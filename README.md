# iot-pi-cam

## Install hardware shutdown

Make script executable with `chmod +x /home/pi/iot-pi-cam/shutdown.py`.

Create a service with `sudo nano /lib/systemd/system/switchoff.service` as root and with content:

```
[Unit]
Description=Shutdown Rasperry With Button
After=multi-user.target

[Service]
Type=idle
ExecStart=/home/pi/iot-pi-cam/shutdown.py &

[Install]
WantedBy=multi-user.target
```
Make service executable `sudo chmod 644 /lib/systemd/system/switchoff.service`, register it and activate it:
```
sudo systemctl daemon-reload
sudo systemctl enable switchoff.service
sudo systemctl start switchoff.service
```
After restart:
```
sudo systemctl status switchoff.service
```
Use `disable` and `stop` to turn it off.

Use `journalctl -u switchoff.service -f` to follow logs


## Install capturing

Make script executable with `chmod +x /home/pi/iot-pi-cam/src/capture.py`.

Create a service with `sudo nano /lib/systemd/system/capture.service` as root and with content:

```
[Unit]
Description=Capture pictures
After=multi-user.target

[Service]
WorkingDirectory=/home/pi/iot-pi-cam/src/
Type=idle
ExecStart=/home/pi/iot-pi-cam/src/capture.py &

[Install]
WantedBy=multi-user.target
```
Make service executable `sudo chmod 644 /lib/systemd/system/capture.service`, register it and activate it:
```
sudo systemctl daemon-reload
sudo systemctl enable capture.service
sudo systemctl start capture.service
```
After restart:
```
sudo systemctl status capture.service
```
Use `disable` and `stop` to turn it off.

Use `journalctl -u capture.service -f` to follow logs


## Install web server

Install requirements with `sudo pip3 install -r /home/pi/iot-pi-cam/src/requirements.txt`

Make script executable with `chmod +x /home/pi/iot-pi-cam/src/index.py`.

Create a service with `sudo nano /lib/systemd/system/web.service` as root and with content:

```
[Unit]
Description=Provide web access to the pictures
After=multi-user.target

[Service]
WorkingDirectory=/home/pi/iot-pi-cam/src/
Type=idle
ExecStart=/home/pi/iot-pi-cam/src/index.py &

[Install]
WantedBy=multi-user.target
```
Make service executable `sudo chmod 644 /lib/systemd/system/web.service`, register it and activate it:
```
sudo systemctl daemon-reload
sudo systemctl enable web.service
sudo systemctl start web.service
```
After restart:
```
sudo systemctl status web.service
```
Use `disable` and `stop` to turn it off.

Use `journalctl -u web.service -f` to follow logs
