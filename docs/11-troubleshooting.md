# 11. Troubleshooting

Problems met while writing this guide, with what caused them.

## ST-Link

**`st-flash`: "Can not connect to target", or `stlink-gui` connects
only sometimes.**
The `stlink` tools are unreliable with these boards. The same adapter
and wiring work with OpenOCD (chapter 2). If OpenOCD reports a target
voltage around 3.2 V and a Cortex-M3, the wiring and power are fine.

**`chipid: 0x000` from `st-info --probe`.**
Another program (for example `stlink-gui`) is still holding the
adapter, or a jumper wire is not seated on the small toolhead header.

## Wi-Fi

**The printer boots but never appears on the network; the log shows
`CTRL-EVENT-ASSOC-REJECT status_code=30`.**
The router is in WPA2/WPA3 mixed mode and the generated Wi-Fi
configuration asks for WPA3 and protected management frames, which the
`rtl8189fs` driver cannot complete. Use the `auth` block with
`key-management: psk` from chapter 3. The generated configuration can
be inspected, without the password line, with:

```
sudo grep --invert-match "psk=" /run/netplan/wpa-wlan1.conf
```

It should contain `key_mgmt=WPA-PSK` and no `ieee80211w` line.

## Klipper start

**Mainsail still shows "mcu 'mcu': Unable to connect" after the new
configuration is installed.**
The message may be left over from the example configuration. Check the
end of `~/printer_data/logs/klippy.log`; if it shows both boards
configured, reload the page or restart the printer.

**A fan does not spin.**
Check it is a fan that has a control at all (section 6.3). A
two-wire fan can be tested by measuring the voltage on its plug while
it is commanded on: about 22 V with no rotation is a dead fan, 0 V is
the output.

## Eddy sensor

**`Failed calibration - No usable data`, with `Frequency too noisy`.**
`max_sensor_hz` is missing or too low for Sovol's coil. Chapter 7.

**`Error during homing probe: Trigger analog error: RAW_RANGE`, with
`Frequency over valid soft range` in `klippy.log`.**
The same cause. Confirm the setting is really in the file Klipper
loads:

```
grep --line-number "max_sensor_hz" ~/printer_data/config/eddy.cfg
```

**`Probe samples exceed samples_tolerance` during a tap, with the
contact heights falling steadily from one sample to the next.**
The nozzle is cooling while it taps, for example right after
`CLEAN_NOZZLE`, which ends with the heater off. Tap at a held
temperature (section 7.4). Samples that scatter up and down point to a
dirty nozzle instead.

**The bed mesh shows a tilt of a millimetre or more.**
The gantry was not levelled after the Z motors were last released.
Run `QUAD_GANTRY_LEVEL`, then `G28 Z`, then the mesh again.

**The nozzle presses on the bed during homing.**
`descend_z` is too small for a nozzle with plastic hanging from it.
Chapter 7 explains the 2.5 mm used here.

## Input shaper

**Prints look over-smoothed, or `SHAPER_CALIBRATE` suggests much lower
accelerations than before, after a slicer calibration print.**
The test left its last shaper values active. Do a Firmware Restart
(section 9.5).

**`MCU 'extra_mcu' shutdown: Timer too close` at the end of
`SHAPER_CALIBRATE`.**
Seen once, with the nozzle heater on. Do a Firmware Restart and run it
with the heaters off (section 9.3).

## Print start

**Plastic is pushed around the nozzle instead of being removed.**
The nozzle was brought near the bed before it was cleaned. Use the
sequence in chapter 8 unchanged, and check `variable_end_retract`.

**Silicone pegs torn from the brush.**
The brush was passed with a cooled nozzle carrying half-set plastic.
The macros in this repository pass it once, at full temperature.

**The nozzle presses hard on the steel strip.**
Raise `variable_pad_z` (chapter 8), judging it at real print starts.

**First layer too close or too far.**
Set the tap offset as described in section 7.6.
