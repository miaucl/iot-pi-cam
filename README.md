# iot-pi-cam

## Install hardware shutdown

Make script executable with `chmod +x </home/pi>/iot-pi-cam/shutdown.py`.

Create a service with `sudo nano /lib/systemd/system/switchoff.iot-pi-cam.service` as root and with content:

```
[Unit]
Description=Shutdown Rasperry With Button
After=multi-user.target

[Service]
Type=idle
ExecStart=</home/pi>/iot-pi-cam/shutdown.py &

[Install]
WantedBy=multi-user.target
```
Make service executable `sudo chmod 644 /lib/systemd/system/switchoff.iot-pi-cam.service`, register it and activate it:
```
sudo systemctl daemon-reload
sudo systemctl enable switchoff.iot-pi-cam.service
sudo systemctl start switchoff.iot-pi-cam.service
```
After restart:
```
sudo systemctl status switchoff.iot-pi-cam.service
```
Use `disable` and `stop` to turn it off.

Use `journalctl -u switchoff.iot-pi-cam.service -f` to follow logs


## Install capturing

Install skimage: https://scikit-image.org/docs/dev/install.html

Make script executable with `chmod +x </home/pi>/iot-pi-cam/src/capture.py`.

Create a service with `sudo nano /lib/systemd/system/capture.iot-pi-cam.service` as root and with content:

```
[Unit]
Description=Capture pictures
After=multi-user.target

[Service]
WorkingDirectory=</home/pi>/iot-pi-cam/src/
Type=idle
ExecStart=</home/pi>/iot-pi-cam/src/capture.py &

[Install]
WantedBy=multi-user.target
```
Make service executable `sudo chmod 644 /lib/systemd/system/capture.iot-pi-cam.service`, register it and activate it:
```
sudo systemctl daemon-reload
sudo systemctl enable capture.iot-pi-cam.service
sudo systemctl start capture.iot-pi-cam.service
```
After restart:
```
sudo systemctl status capture.iot-pi-cam.service
```
Use `disable` and `stop` to turn it off.

Use `journalctl -u capture.iot-pi-cam.service -f` to follow logs


## Install web server

Install requirements with `sudo pip3 install -r </home/pi>/iot-pi-cam/src/requirements.txt`

Make script executable with `chmod +x </home/pi>/iot-pi-cam/src/index.py`.

Create a service with `sudo nano /lib/systemd/system/web.iot-pi-cam.service` as root and with content:

```
[Unit]
Description=Provide web access to the pictures
After=multi-user.target

[Service]
WorkingDirectory=</home/pi>/iot-pi-cam/src/
Type=idle
ExecStart=</home/pi>/iot-pi-cam/src/index.py &

[Install]
WantedBy=multi-user.target
```
Make service executable `sudo chmod 644 /lib/systemd/system/web.iot-pi-cam.service`, register it and activate it:
```
sudo systemctl daemon-reload
sudo systemctl enable web.iot-pi-cam.service
sudo systemctl start web.iot-pi-cam.service
```
After restart:
```
sudo systemctl status web.iot-pi-cam.service
```
Use `disable` and `stop` to turn it off.

Use `journalctl -u web.iot-pi-cam.service -f` to follow logs

## To clear the logs and images

Make clear script executable `sudo chmod x ./clear.sh` and execute it with `./clear.sh`.
