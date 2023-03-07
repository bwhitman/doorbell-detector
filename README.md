# doorbell-detector

A quick sensor to detect a doorbell ringing and alert you, using audioset

## how-to

get an rpi4 + usb microphone, this one works great https://www.amazon.com/gp/product/B08F2BCS96/

install 64bit kernel on the pi: https://qengineering.eu/install-raspberry-64-os.html

install tf 2.2 on the pi: https://qengineering.eu/install-tensorflow-2.2.0-on-raspberry-64-os.html

install the models repo https://github.com/tensorflow/models

do the audioset / yamnet setup https://github.com/tensorflow/models/blob/master/research/audioset/yamnet/README.md

## if you want homekit integration to get alerts

if you want homekit integration, set up homebridge: https://github.com/homebridge/homebridge/wiki/Install-Homebridge-on-Raspbian

and install the "Homebridge Http Motion Sensor" plugin and set it up with this json

```
{
    "accessory": "http-motion-sensor",
    "name": "Sound sensor",
    "port": 18089,
    "serial": "E642021F3ECB",
    "bind_ip": "0.0.0.0"
}
```

restart homebridge

## boot on startup
pip install -r requirements.txt

put `doorbell.py` in `models/research/audioset/yamnet` and then add it in /etc/rc.local like

`sudo -H -u pi /usr/bin/python3 /home/pi/models/research/audioset/yamnet/doorbell.py`

restart the pi

ring your doorbell



