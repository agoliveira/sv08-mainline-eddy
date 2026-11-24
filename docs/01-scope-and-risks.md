# 1. Scope, requirements and risks

## Which printer this is for

- Sovol SV08, original version with the USB toolhead
- Sovol's official Eddy Current Scanning Kit installed and working on
  Sovol's firmware (the kit's 2.4.9 eddy firmware)
- Otherwise stock

The kit's sensor is a bare LDC1612 coil wired by I2C to the toolhead
board. It has no micro-controller of its own, so there is nothing to
flash on the sensor. A BTT Eddy or a Cartographer is a different
device and needs a different configuration.

## What you need

- An ST-Link V2 (a clone is fine) and four jumper wires
- An eMMC module and an eMMC to USB reader. **32 GB is strongly
  recommended.** The stock 8 GB module does boot this system, but the
  complete installation described here occupies close to 6 GB before a
  single G-code file or timelapse is stored.
- A Linux PC with `openocd`, `xz` and an SSH client. Everything in
  this guide was done from Linux; Windows was not tested. If you work
  from Windows, [Rappetor's guide](https://github.com/Rappetor/Sovol-SV08-Mainline) describes writing the eMMC and
  flashing the boards with Windows tools, and the values used here
  (image, sizes, firmware settings) still apply.
- For the unlucky case only: a USB keyboard, to use with the printer's
  HDMI screen if the first boot does not join your Wi-Fi

Keep the original eMMC module untouched if you can, and install onto a
second one. Swapping modules is then your way back on the host side.

## Risks

- Both boards are reflashed. After that, Sovol's system no longer
  talks to them until their original firmware is written back with the
  ST-Link (chapter 10). A spare eMMC alone does not undo this.
- The nozzle touches the bed on purpose during "tap". A wrong
  threshold or a dirty nozzle gives a wrong Z reference. Follow the
  calibration order in chapter 7 and stay near the emergency stop the
  first times.
- Swapping the two board serial numbers in `printer.cfg` makes Klipper
  drive the wrong pins. Chapter 5 shows how to tell the boards apart
  and chapter 6 how to confirm it before any heater is used.
- Sovol's support will not cover a printer running this.

## How long

Allow most of a day the first time. The steps with waiting are the
eMMC image backup (about 25 minutes for 32 GB) and the package
installations on the printer.
