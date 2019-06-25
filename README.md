# iot-pi-cam

## Install hardware shutdown

Make script executable with `chmod +x /home/pi/iot-pi-cam/shutdown.py`.

Create a service in `/lib/systemd/system/` (as root) with name "switchoff.service" and content:

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
Use `disable` to turn it off.

## Install tools

Docker: https://sebastianbrosch.blog/docker-auf-einem-raspberry-pi-3-installieren/
To avoid using root access: `sudo usermod -a -G docker pi`
Git
