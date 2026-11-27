# 7. The eddy sensor

Sovol's kit is an LDC1612 coil on the toolhead board's I2C pins
(`PB6` clock, `PB7` data). Klipper's native `[probe_eddy_current]`
drives it with three settings that differ from a generic setup. They
are already in `config/eddy.cfg`:

```
[probe_eddy_current eddy]
sensor_type: ldc1612
i2c_mcu: extra_mcu
i2c_software_scl_pin: extra_mcu:PB6
i2c_software_sda_pin: extra_mcu:PB7
descend_z: 2.5
max_sensor_hz: 10000000
x_offset: -16.43
y_offset: 10.22
```

- **Software I2C.** The hardware I2C bus of this STM32F103 toolhead
  can lock up under mainline firmware. Software I2C on the same two
  pins works.
- **`max_sensor_hz: 10000000`.** Sovol's coil resonates near 8.5 MHz.
  Klipper assumes at most 5 MHz by default and sets the chip's input
  divider from that, which puts the chip outside its valid range. The
  symptom is a height calibration that ends with `Failed calibration -
  No usable data`, and homing that fails with `Trigger analog error:
  RAW_RANGE`.
- **`descend_z: 2.5`.** The height at which contactless homing and
  probing stop. Klipper suggests 0.5 mm. That leaves no room for
  plastic hanging from a nozzle that has not been cleaned yet: at 0.5
  mm a hard remnant is pressed into the plate by the Z motors. Sovol's
  firmware stops at about 2.6 mm. Precise Z does not come from this
  height; it comes from the tap.

The X and Y offsets are Sovol's, for the kit's own mount.

## 7.1 Drive current

Z cannot be homed yet, so the sensor is positioned by eye. In the
Mainsail console:

```
G28 X Y
```

```
G0 X191 Y165 F6000
```

Measure the distance from the sensor to the bed with a ruler and tell
Klipper (here for 62 mm), then bring the sensor to 20 mm:

```
SET_KINEMATIC_POSITION Z=62
```

```
G0 Z20 F600
```

```
LDC_CALIBRATE_DRIVE_CURRENT CHIP=eddy
```

It reports a `reg_drive_current` value (21 here; Sovol's firmware used
22 on the same sensor). An error at this step instead means the sensor
is not answering on I2C.

```
SAVE_CONFIG
```

## 7.2 Height calibration

Clean the nozzle tip and have a sheet of ordinary paper ready.

```
G28 X Y
```

```
G0 X191 Y165 F6000
```

```
SET_KINEMATIC_POSITION Z=30
```

The `Z=30` is deliberately more than the real height, so Klipper lets
the nozzle travel down to the bed.

```
PROBE_EDDY_CURRENT_CALIBRATE CHIP=eddy
```

Lower the nozzle by eye; the Z value displayed is not the real height:

```
TESTZ Z=-1
```

```
TESTZ Z=-0.1
```

Do the paper test (the paper drags lightly but still moves), then:

```
ACCEPT
```

Keep clear: the toolhead moves the sensor over the same spot and runs
Z movements for a couple of minutes. A good result looks like this:

```
probe_eddy_current: noise 0.003101mm, MAD_Hz=34.809 in 4041 queries
Total frequency range: 56145.072 Hz
```

```
SAVE_CONFIG
```

## 7.3 Homing and gantry levelling

Bed clear, emergency stop at hand:

```
G28
```

The nozzle stops about 2.5 mm above the bed center, then rises to
10 mm.

```
QUAD_GANTRY_LEVEL
```

It should converge within its retries to a range under 0.05 mm.

The gantry loses its level whenever the Z motors are released, which
includes every Klipper restart. `G28` does not restore it. Always run
`QUAD_GANTRY_LEVEL` before judging a bed mesh; a mesh taken without it
shows a tilt of a millimetre or more that is not the bed.

## 7.4 Tap

The nozzle touches the bed in this step. Nozzle and bed must be clean,
nozzle cold. `[stepper_z]` already has `position_min: -2`, which tap
needs.

Tap only at a stable nozzle temperature: fully cold, as here, or held
at a set temperature, as `START_PRINT` does. A nozzle that is cooling
down shrinks between samples. Here that showed as contact heights
falling by about 0.02 mm per tap, and Klipper rejecting them with
`Probe samples exceed samples_tolerance`.

```
G28 Z
```

```
G0 Z5 F600
```

```
PROBE_EDDY_CURRENT_TAP_CALIBRATE TAP=guess
```

The nozzle should touch the bed lightly, lift, and report a contact
height. Use the emergency stop if it keeps pressing instead of
lifting. Then:

```
G0 Z5 F600
```

```
PROBE_EDDY_CURRENT_TAP_CALIBRATE TAP=refine
```

```
G0 Z5 F600
```

```
PROBE_EDDY_CURRENT_TAP_CALIBRATE TAP=verify
```

`verify` taps five times. Here the five results were within 0.008 mm
of each other, with a threshold of about 5400.

```
SAVE_CONFIG
```

If a stage fails, Klipper's
[eddy probe documentation](https://www.klipper3d.org/Eddy_Probe.html#tap-calibration)
describes how to find a threshold by hand.

## 7.5 Bed mesh

```
QUAD_GANTRY_LEVEL
```

```
G28 Z
```

```
BED_MESH_CALIBRATE METHOD=rapid_scan
```

Compared on the same bed, 41 by 41 points:

| Method | Time | Range measured |
|---|---|---|
| `rapid_scan` | under a minute | 0.423 mm |
| `scan` | 5 to 6 minutes | 0.417 mm |

The two agreed within 0.006 mm, so `rapid_scan` is the default in the
print start macro.

## 7.6 The tap offset, after the first print

The tap is done at 150 °C and printing happens hotter, so the first
layer usually comes out slightly too close. Correct it once:

1. During a first layer, adjust the height with Mainsail's Z-offset
   buttons until it is right. Here that was +0.1 mm.
2. With that offset still active (before the next print starts, and
   before any restart):

```
Z_OFFSET_APPLY_PROBE METHOD=tap
```

```
SAVE_CONFIG
```

This stores the correction as `tap_z_offset` (here `-0.100`). The
`METHOD=tap` part is essential: without it the command shifts the
sensor's height table instead.

Whether one value suits filaments printed at very different
temperatures was not tested.
