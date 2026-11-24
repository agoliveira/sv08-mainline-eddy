# 4. Klipper stack, touch screen and camera

All commands in this chapter run on the **printer**.

## 4.1 KIAUH

```
cd ~ && git clone https://github.com/dw-0/kiauh.git
```

```
~/kiauh/kiauh.sh
```

Accept the offer to use the current version if asked. From the
**Install** menu, install these one at a time, in this order:

1. **Klipper**: Python 3, one instance, and yes to adding the user to
   the `tty` and `dialout` groups.
2. **Moonraker**: yes to the instance and to the PolicyKit rules.
3. **Mainsail**: default port, yes to Mainsail-Config (it provides
   `mainsail.cfg` with the standard pause, resume and cancel macros),
   yes to the update manager entry.
4. **KlipperScreen**, if you have the HDMI touch screen: choose the
   Xserver backend. **Answer no to installing NetworkManager.** The
   Wi-Fi was set up with netplan in chapter 3, and a second network
   manager could take the interface over. Only KlipperScreen's own
   network panel is lost.
5. **Crowsnest**, if you have the camera. It asks for a reboot at the
   end: accept.

KIAUH's menu numbers change between versions; go by the names.

Open `http://PRINTER_ADDRESS` in a browser. Mainsail loads and reports
that Klipper cannot connect to its micro-controller. That is the
expected state until chapter 5 is done.

## 4.2 Touch screen orientation

The 5 inch HDMI screen is mounted upside down on the SV08. Picture and
touch are rotated separately.

Find the output name (it was `HDMI-1` here):

```
DISPLAY=:0 xrandr --query | grep " connected"
```

Rotate the picture:

```
sudo mkdir --parents /etc/X11/xorg.conf.d
```

```
sudo mcedit /etc/X11/xorg.conf.d/90-monitor.conf
```

```
Section "Monitor"
    Identifier "HDMI-1"
    Option "Rotate" "inverted"
EndSection
```

Rotate the touch input to match:

```
sudo mcedit /etc/X11/xorg.conf.d/91-touch-rotate.conf
```

```
Section "InputClass"
    Identifier "Touchscreen rotate 180"
    MatchIsTouchscreen "on"
    Option "TransformationMatrix" "-1 0 1 0 -1 1 0 0 1"
EndSection
```

```
sudo systemctl restart KlipperScreen
```

## 4.3 Camera

On this kernel the camera is not `/dev/video0` as in Sovol's
configuration. Use its stable name instead:

```
ls -l /dev/v4l/by-id/
```

Take the entry ending in `-video-index0` and put it in Crowsnest's
configuration:

```
mcedit ~/printer_data/config/crowsnest.conf
```

In the `[cam 1]` section, with your own device name:

```
device: /dev/v4l/by-id/YOUR_CAMERA-video-index0
resolution: 1280x720
max_fps: 15
```

```
sudo systemctl restart crowsnest
```

Sovol's bed camera offers MJPEG up to 1280x720 at 30 frames per
second, so the host only passes frames through. To see what yours
supports:

```
sudo apt-get --yes install v4l-utils
```

```
v4l2-ctl --device=/dev/v4l/by-id/YOUR_CAMERA-video-index0 --list-formats-ext
```

The stream is at `http://PRINTER_ADDRESS/webcam/?action=stream`.
