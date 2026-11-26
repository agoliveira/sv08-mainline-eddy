# Sovol SV08 with the official eddy kit, on mainline Klipper

A step-by-step guide and a set of configuration files for running a
Sovol SV08 fitted with **Sovol's official Eddy Current Scanning Kit** on
unmodified mainline Klipper, using Klipper's native `probe_eddy_current`
support with "tap". No eddy-ng, no patched Klipper.

## Why

Sovol's firmware for the eddy kit is a modified, old Klipper that cannot
be updated. Existing community guides for the SV08 cover the stock probe
or the BTT Eddy, and route the Sovol kit through eddy-ng. Since late
2025 mainline Klipper has its own tap support, and it works with this
sensor once two settings are known:

- the sensor must use **software I2C** on the toolhead board, and
- `max_sensor_hz` must be raised, because Sovol's coil resonates near
  8.5 MHz and Klipper's default assumes less than 5 MHz.

## What you end up with

- Armbian (Debian 13) on the printer's host, installed headless
- Mainline Klipper, Moonraker, Mainsail, KlipperScreen on the HDMI
  touch screen, the knob LCD, and the camera
- Katapult on both boards, so later firmware updates need no ST-Link
- Contactless homing, gantry levelling and fast mesh scanning with the
  eddy sensor, and nozzle "tap" for the Z reference at every print
- A print start sequence with nozzle cleaning, adaptive mesh and an
  adaptive purge line

## What you lose

- Sovol's power-loss recovery
- Sovol's Z-offset calibration routine and the pressure plate under the
  bed (the tap replaces both)
- Sovol's menu on the knob LCD (Klipper's standard menu is used)

## Status

Everything here was carried out on **one printer**, in November 2026,
with Klipper v0.14.0 and Armbian 26.11 (kernel 6.18). Treat it as one
person's verified notes, not as a tested product.

All the work on the PC side was done on Linux machines. **Windows was
not tested**, and the PC commands in this guide are Linux commands.
For Windows, including flashing the boards with STM32CubeProgrammer,
and for photos of the connectors and pinouts, see
[Rappetor's guide](https://github.com/Rappetor/Sovol-SV08-Mainline).

Not verified, and marked as such where they appear:

- Cura (only OrcaSlicer was used)
- The exhaust fan of the enclosure kit
- Restoring the stock firmware (the backups were made and checked, the
  restore itself was not needed)
- Day-to-day use of an 8 GB eMMC (it boots, see chapter 3)
- Updating Klipper later and reflashing the two boards afterwards
  (section 5.7)

## Chapters

1. [Scope, requirements and risks](docs/01-scope-and-risks.md)
2. [Backups](docs/02-backups.md)
3. [Host system: Armbian](docs/03-host-armbian.md)
4. [Klipper stack, touch screen and camera](docs/04-klipper-stack.md)
5. [Firmware on the two boards](docs/05-mcu-firmware.md)
6. [Configuration and first start](docs/06-configuration.md)
7. [The eddy sensor](docs/07-eddy-sensor.md)
8. [Print start sequence and slicer](docs/08-print-start.md)
9. [Input shaper](docs/09-input-shaper.md)
10. [Going back to Sovol's firmware](docs/10-rollback.md)
11. [Troubleshooting](docs/11-troubleshooting.md)
12. [Extras](docs/12-extras.md): beeper signals, temperature-controlled
    mainboard fan

The configuration files are in [`config/`](config/). Optional
additions are in [`extras/`](extras/) and described in chapter 12.

## Conventions

Commands are written out in full. A few values are specific to your
printer and are written in capitals; replace them with your own:

- `PRINTER_ADDRESS`: the printer's IP address on your network
- `MAINBOARD_SERIAL`, `TOOLHEAD_SERIAL`: the serial numbers of the two
  boards, found in chapter 5
- `YOUR_WIFI_NAME`, `YOUR_WIFI_PASSWORD`, `YOUR_ROOT_PASSWORD`

Each command block says where it runs: on your **PC** (Linux; Windows
was not tested, see Status) or on the **printer** (over SSH).

## Credits

- [Rappetor/Sovol-SV08-Mainline](https://github.com/Rappetor/Sovol-SV08-Mainline),
  the reference guide for mainline Klipper on the SV08. The Katapult
  and firmware settings, the board pin assignments and the knob LCD
  configuration used here come from it.
- The [Klipper documentation](https://www.klipper3d.org/Eddy_Probe.html)
  on eddy current probes.
- The Armbian maintainer of the Sovol SV08 board support.
- Sovol, whose stock configuration these files were converted from.

## Changes

See [CHANGELOG.md](CHANGELOG.md).

## License

GPL-3.0. See [LICENSE](LICENSE).
