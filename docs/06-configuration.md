# 6. Configuration and first start

## 6.1 The files

| File | Content |
|---|---|
| `printer.cfg` | Boards, motion, heaters, fans, sensors, accelerometer |
| `eddy.cfg` | Eddy sensor, bed mesh, gantry levelling, homing order |
| `lcd.cfg` | Knob LCD, beeper, LCD backlight |
| `macros.cfg` | Print start and end, nozzle cleaning, tap, purge, filament |

They are Sovol's stock configuration for the eddy kit, converted. Pin
assignments, motor currents, thermistor tables and PID values are
Sovol's. Differences that matter:

- **Eddy sensor** on Klipper's native driver. Chapter 7.
- **Hotend `min_temp: 5`.** Sovol ships `-250`, which disables the
  check for a broken or unplugged thermistor.
- **The two part cooling fans are one native `[fan]`**, so `M106` and
  `M107` work without macros.
- **The mainboard fan** runs while a heater or the X/Y motors are
  active and for five minutes after, instead of always.
- **`max_accel: 20000`** instead of 40000. Chapter 9.
- **Idle timeout of 30 minutes.** Sovol's value amounts to about 69
  days, so heaters left on stayed on. After 30 idle minutes the motors
  are released and the heaters switched off, except while a print is
  paused.
- **Removed:** Sovol's Z-offset calibration, power-loss recovery and
  the macros that call shell scripts.

## 6.2 Install

Copy the four files from `config/` in this repository to the printer.
On the **PC**, from the repository directory:

```
scp config/printer.cfg config/eddy.cfg config/lcd.cfg config/macros.cfg sovol@PRINTER_ADDRESS:/home/sovol/printer_data/config/
```

This replaces the example `printer.cfg` that KIAUH created.

On the **printer**, put your two serial numbers from chapter 5 in
place:

```
mcedit ~/printer_data/config/printer.cfg
```

```
[mcu]
serial: /dev/serial/by-id/usb-Klipper_stm32f103xe_MAINBOARD_SERIAL-if00

[mcu extra_mcu]
serial: /dev/serial/by-id/usb-Klipper_stm32f103xe_TOOLHEAD_SERIAL-if00
```

If your printer has values of its own that differ from stock (PID
values after a hotend change, for example), carry them over from your
backup of Sovol's `printer.cfg`.

```
sudo systemctl start klipper
```

Open Mainsail. If it still shows an old connection error, reload the
page or restart the printer; the state should be `Standby`.

## 6.3 First-start checks

Do these in order, before homing or heating anything.

**Temperatures.** Extruder and bed must both read room temperature and
agree within a few degrees. This is the confirmation that the two
serial numbers are not swapped: a swapped pair puts a thermistor on a
pin with nothing connected, and Klipper stops with a temperature
error.

**Fans and light.** In Mainsail's Miscellaneous panel:

- `Fan` at 100%: both part cooling fans spin (the one at the back of
  the toolhead and the one in the cover).
- `Main Led`: the light follows the slider.

The hotend fan has no slider. It switches on by itself above 45 °C.
It and the mainboard fan spin briefly at power-up and stop when
Klipper connects; that is by design.

**Endstops.** With the toolhead away from the right and back ends of
its travel:

```
QUERY_ENDSTOPS
```

Expected: `stepper_x:open stepper_y:open stepper_z:open`.

**Homing X and Y.** Gantry at mid height, bed clear, emergency stop at
hand:

```
G28 X Y
```

The gantry lifts 5 mm, the toolhead homes to the back, then to the
right. Each axis must stop cleanly on contact. Do not home Z yet: the
eddy sensor has to be calibrated first.

## 6.4 The exhaust fan

Sovol's enclosure kit adds an exhaust fan on mainboard pin `PA2`. Its
section is present but commented out in `printer.cfg`, with a matching
commented line in the `_ALL_FAN_OFF` macro. It was not tested.

## 6.5 Keep a copy of your configuration

All calibration results are stored at the end of `printer.cfg`. After
chapters 7 to 9, and whenever `SAVE_CONFIG` has changed something you
care about, copy the configuration to the **PC**:

```
ssh sovol@PRINTER_ADDRESS "tar --create --gzip --file=- --directory=/home/sovol printer_data/config" > sv08-mainline-config.tar.gz
```
