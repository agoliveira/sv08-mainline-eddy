# 9. Input shaper

Sovol's configuration carries the same placeholder for both axes
(MZV at 35 Hz) and only tests between 20 and 40 Hz. The toolhead's
accelerometer works on mainline firmware, so the real values can be
measured.

## 9.1 Check the accelerometer

In the Mainsail console:

```
ACCELEROMETER_QUERY
```

It answers with three numbers; one of them is near 9800 (gravity).

## 9.2 Install NumPy

On the **printer**. Klipper's documentation says to install
`numpy<1.26`. Those versions do not support the Python 3.13 that
Debian 13 provides, so the current version is installed instead:

```
sudo apt-get --yes install python3-numpy python3-matplotlib libopenblas-dev
```

```
~/klippy-env/bin/pip install numpy
```

```
~/klippy-env/bin/python -c "import numpy; print(numpy.__version__)"
```

Restart Klipper afterwards (Firmware Restart in Mainsail).

## 9.3 Measure

Fit the toolhead exactly as you print with it, cover included, and
remove anything loose from the printer.

Run it with all heaters off, and do a Firmware Restart first if
anything was printed since the last restart. With the nozzle heater
on, the toolhead board shut down once here with `Timer too close` at
the moment the calculation started. The results were still valid.

```
G28
```

```
SHAPER_CALIBRATE
```

It vibrates each axis for a few minutes and prints a recommendation
per axis. Then:

```
SAVE_CONFIG
```

On the printer this guide comes from:

| Axis | Placeholder | Recommended |
|---|---|---|
| X | MZV 35 Hz | MZV 57.6 Hz |
| Y | MZV 35 Hz | MZV 41.2 Hz |

Your values will differ; measure your own.

The configuration in this repository leaves out Sovol's
`damping_ratio_x: 0.001` and `damping_ratio_y: 0.001`. Klipper's
default is 0.1, and its calibration evaluates shapers around that
value. Section 9.5 describes how to measure it.

## 9.4 Acceleration

The calibration also prints, per axis, the acceleration above which
the shaper starts to soften fine detail. Here that was about 9800
mm/s² on X and 5000 mm/s² on Y. These are quality guides for visible
surfaces, not limits: infill and travel can go much higher.

`max_accel` in `printer.cfg` is only a ceiling, set to 20000 here
instead of Sovol's 40000. What is actually used comes from the slicer.
For sharp outer walls, set the slicer's outer wall acceleration at or
below the lower of your two figures.

These figures depend on the damping ratio in effect, which is one more
reason to read them after a clean restart.

## 9.5 Damping ratio and slicer tests

`SHAPER_CALIBRATE` finds the shaper type and frequency. It does not
measure the damping ratio, and Klipper uses 0.1 unless told otherwise.
A slicer's damping test can find a better value (OrcaSlicer has one in
its Calibration menu):

- Enter the frequencies the accelerometer gave. Do not take the
  frequencies from a printed tower in their place: here the tower's
  did not match the accelerometer's, which gave the same result on
  three runs.
- Read each wall by the letter on it. The wall marked X runs along the
  Y axis; that is by design.
- Pick the height where the ripples after a corner are weakest. If a
  wall looks the same over a wide range, keep 0.1 for that axis.
- Put the result in `printer.cfg`, in `[input_shaper]`, as
  `damping_ratio_x` and `damping_ratio_y`. Not in the start G-code.

Here that gave 0.171 for X, and Y stayed at 0.1.

**These test prints leave the printer altered.** They set the shaper
with `SET_INPUT_SHAPER`, and the last value stays active until Klipper
restarts. Here the printer was left with a damping ratio of 0.4 on
both axes. Do a Firmware Restart after any slicer calibration print.
