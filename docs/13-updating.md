# 13. Updating

Being able to update is the reason for this whole exercise. This
chapter is based on one update: Klipper `v0.14.0-0` to `v0.14.0-1`, a
single host-side change. Both boards were reflashed afterwards on
purpose, to prove that it works over USB.

## 13.1 Before updating

Copy the configuration to the PC (section 6.5).

On the **printer**, record the version you are on. This is the point
to return to if the new one misbehaves:

```
git -C ~/klipper rev-parse HEAD
```

Look at what the update will change:

```
git -C ~/klipper log --oneline HEAD..origin/master
```

```
git -C ~/klipper diff --stat HEAD..origin/master
```

Files under `src/` and `lib/` are board firmware. If
`klippy/extras/probe_eddy_current.py` or `klippy/extras/ldc1612.py`
are in the list, read Klipper's
[configuration changes](https://www.klipper3d.org/Config_Changes.html)
before going on: the eddy support is recent, and an option was already
renamed once (`z_offset` became `descend_z`).

## 13.2 Update the host

In Mainsail, open the Machine tab and its Update Manager. Update one
component at a time, starting with `klipper`. Do not use "Update all
components": with one change at a time, a problem has one suspect.

Klipper restarts by itself. The state must come back to `Ready`.

Mainsail showed no notice about the firmware of the boards after this
update. Do not wait for one.

KlipperScreen was updated the same way afterwards. The screen and
touch rotation from chapter 4 were kept.

The note "Repo has untracked source files" on the `moonraker` line
comes from the timelapse plugin, which installs a file there. It is
informational.

Updating the operating system packages from this panel was not
exercised.

## 13.3 When the boards need new firmware

It is required when Klipper refuses to start after an update with an
`MCU Protocol error`, which says that the firmware on a board is older
than the host software.

Otherwise it is optional. Reflashing keeps the host and both boards on
the same version, which the Machine tab shows for each of them.

## 13.4 Reflash the boards over USB

No ST-Link is needed: Klipper hands each board over to Katapult on
request. The printer must be idle and cool. The mainboard fan and the
light go off while the mainboard is in the bootloader.

Use your own serial numbers from chapter 5. Each block is one chain:
if any step fails, the rest does not run, so a failed build can never
put one board's firmware on the other.

On the **printer**, the mainboard:

```
sudo systemctl stop klipper && \
cd ~/klipper && \
make clean KCONFIG_CONFIG=config.mainboard && \
make olddefconfig KCONFIG_CONFIG=config.mainboard && \
make KCONFIG_CONFIG=config.mainboard --jobs=4 && \
~/klippy-env/bin/python ~/katapult/scripts/flashtool.py --request-bootloader --device /dev/serial/by-id/usb-Klipper_stm32f103xe_MAINBOARD_SERIAL-if00 && \
sleep 2 && \
~/klippy-env/bin/python ~/katapult/scripts/flashtool.py --firmware ~/klipper/out/klipper.bin --device /dev/serial/by-id/usb-katapult_stm32f103xe_MAINBOARD_SERIAL-if00
```

Then the toolhead:

```
cd ~/klipper && \
make clean KCONFIG_CONFIG=config.toolhead && \
make olddefconfig KCONFIG_CONFIG=config.toolhead && \
make KCONFIG_CONFIG=config.toolhead --jobs=4 && \
~/klippy-env/bin/python ~/katapult/scripts/flashtool.py --request-bootloader --device /dev/serial/by-id/usb-Klipper_stm32f103xe_TOOLHEAD_SERIAL-if00 && \
sleep 2 && \
~/klippy-env/bin/python ~/katapult/scripts/flashtool.py --firmware ~/klipper/out/klipper.bin --device /dev/serial/by-id/usb-katapult_stm32f103xe_TOOLHEAD_SERIAL-if00
```

Each must show `Bootloader Request Complete` and end with
`Programming Complete`. Then:

```
ls -l /dev/serial/by-id/
```

```
sudo systemctl start klipper
```

Both entries must start with `usb-Klipper_stm32f103xe_` again.

`make olddefconfig` carries the saved build settings over to the new
version. If a later Klipper adds build options that matter, run
`make menuconfig` with the same `KCONFIG_CONFIG` and compare with the
tables in chapter 5.

If a chain stops after the bootloader request, the board is waiting in
Katapult and is listed as `usb-katapult_stm32f103xe_`. Nothing is
lost: run the last command of the chain again, with the firmware of
that board in `out/`.

## 13.5 Verify

Bed clear. In the Mainsail console, one line at a time:

```
G28
```

```
QUAD_GANTRY_LEVEL
```

```
G28 Z
```

```
M109 S150
```

```
G4 P30000
```

```
TAP_HOME
```

```
BED_MESH_CALIBRATE METHOD=rapid_scan
```

```
M104 S0
```

The nozzle must be clean for the tap. It is held at 150 °C, with a 30
second wait, because a tap on a nozzle that is still cooling drifts
(section 7.4).

The gantry level must converge, `TAP_HOME` must report a bed surface
height, and the mesh must look like your usual one. In the Machine
tab, `mcu` and `extra_mcu` must show the same version as the host.

## 13.6 Going back

**Not exercised.** The update done here needed no return.

On the **printer**, with the commit recorded in 13.1:

```
sudo systemctl stop klipper
```

```
git -C ~/klipper checkout YOUR_RECORDED_COMMIT
```

```
sudo systemctl start klipper
```

If the boards were reflashed with the newer version and Klipper now
reports a protocol error, reflash them as in 13.4; the build then
comes from the older source. Restore the configuration from your copy
if the update made you change it.

The update manager shows the repository as modified while it sits on
an older commit. To follow updates again later:

```
git -C ~/klipper checkout master
```
