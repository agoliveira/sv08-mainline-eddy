# 3. Host system: Armbian

Armbian has an official community image for the SV08's host board, with
its own device tree. No boot files need editing.

## 3.1 Download and verify

On the **PC**:

```
wget --output-document=armbian-sv08-trixie.img.xz https://dl.armbian.com/sovol-sv08/Trixie_current_minimal
```

```
wget --output-document=armbian-sv08-trixie.img.xz.sha https://dl.armbian.com/sovol-sv08/Trixie_current_minimal.sha
```

```
sha256sum armbian-sv08-trixie.img.xz
```

```
cat armbian-sv08-trixie.img.xz.sha
```

The hash printed by `sha256sum` must equal the first field of the
`.sha` file.

## 3.2 Write the image

Put the target eMMC module in the reader. If it is the module you
imaged in chapter 2, this erases it: make sure that image was verified.

Identify the device as in chapter 2 and replace `sdX`:

```
lsblk --output NAME,SIZE,MODEL,TRAN,MOUNTPOINTS
```

```
sudo umount /dev/sdX1 /dev/sdX2
```

```
xz --decompress --stdout armbian-sv08-trixie.img.xz | sudo dd of=/dev/sdX bs=4M conv=fsync status=progress
```

Unplug the reader and plug it back in, so the new partitions are seen:

```
lsblk --output NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS /dev/sdX
```

There are two partitions, labelled `BOOT` and `armbi_root`. Mount the
second one at a known place:

```
sudo mkdir --parents /mnt/sv08root
```

```
sudo mount /dev/sdX2 /mnt/sv08root
```

## 3.3 Prepare a headless first boot

Two files make the printer come up on your Wi-Fi with a user account,
without a keyboard.

**User, password, locale.** The file exists and is empty; it is read at
first boot:

```
sudo mcedit /mnt/sv08root/root/.not_logged_in_yet
```

Content. Adjust the time zone, and replace the root password:

```
PRESET_NET_CHANGE_DEFAULTS="0"
PRESET_CONNECT_WIRELESS="n"
SET_LANG_BASED_ON_LOCATION="n"
PRESET_LOCALE="en_US.UTF-8"
PRESET_TIMEZONE="Etc/UTC"
PRESET_ROOT_PASSWORD="YOUR_ROOT_PASSWORD"
PRESET_USER_NAME="sovol"
PRESET_USER_PASSWORD="sovol"
PRESET_DEFAULT_REALNAME="Sovol"
PRESET_USER_SHELL="bash"
```

The user is named `sovol` so that the paths match what other SV08
material assumes (`/home/sovol/printer_data`). Change the password
after the first login.

**Wi-Fi.** Armbian's own Wi-Fi preset is deliberately not used. The
configuration it generates asks for WPA3 and protected management
frames when the router offers them, and the Wi-Fi driver on this board
(`rtl8189fs`) then fails to associate with routers in WPA2/WPA3 mixed
mode. Writing the file by hand, with key management fixed to WPA2,
works with both plain WPA2 and mixed-mode routers.

```
sudo mcedit /mnt/sv08root/etc/netplan/30-wifis-dhcp.yaml
```

Content. Use spaces only, no tabs, keep the quotes, and set your
country code:

```
network:
  wifis:
    wlan1:
      dhcp4: yes
      dhcp6: yes
      regulatory-domain: US
      access-points:
        "YOUR_WIFI_NAME":
          auth:
            key-management: psk
            password: "YOUR_WIFI_PASSWORD"
```

The driver creates two interfaces, `wlan0` and `wlan1`. `wlan1` is the
one Armbian's own setup selected on the printer this guide comes from.

```
sudo chmod 600 /mnt/sv08root/etc/netplan/30-wifis-dhcp.yaml
```

```
sudo umount /mnt/sv08root
```

If the desktop also mounted the partitions by itself, unmount those
too before unplugging the reader.

## 3.4 First boot

Fit the module in the printer (mind the orientation arrow on the
board, both screws) and switch on. The first boot expands the
filesystem; allow five minutes. The fans, the light and the knob LCD
do nothing useful yet.

Find the printer's address in your router's client list (the host
name is `sovol-sv08`) and log in from the **PC**:

```
ssh sovol@PRINTER_ADDRESS
```

If SSH complains that the host key changed, because the address was
used by the Sovol system before:

```
ssh-keygen -R PRINTER_ADDRESS
```

**If it does not appear on the network:** connect a USB keyboard and
look at the HDMI screen. It will be at a root prompt. These three
commands, in order, show whether the Wi-Fi hardware is seen, what was
configured, and why the connection fails:

```
ip -brief address
```

```
cat /etc/netplan/30-wifis-dhcp.yaml
```

```
journalctl --unit=netplan-wpa-wlan1 --no-pager --lines=20
```

`ASSOC-REJECT status_code=30` in that log is the mixed-mode problem
described above: check that the `auth` block is present and correctly
indented, then run `netplan apply`.

## 3.5 Base setup

On the **printer**. First replace the password of the `sovol` user,
which section 3.3 set to `sovol`:

```
passwd
```

A host name of your choice (here `sv08`):

```
sudo hostnamectl set-hostname sv08
```

```
sudo sed --in-place "s/sovol-sv08/sv08/g" /etc/hosts
```

Updates and two tools used later:

```
sudo apt-get update && sudo apt-get --yes full-upgrade && sudo apt-get --yes install git mc
```

```
sudo reboot
```

After logging back in, check the clock, which matters for package
installation and for Moonraker's update checks:

```
timedatectl status
```

`System clock synchronized: yes` may take a minute after boot.

## About the 8 GB module

This image was booted from the stock 8 GB eMMC as a test and came up
normally. That is all that was tested on it. The complete installation
in the following chapters uses close to 6 GB, which leaves very little
for G-code files, timelapse frames and system updates. Use a larger
module.
