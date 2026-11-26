# 8. Print start sequence and slicer

## 8.1 What START_PRINT does

`START_PRINT`, called with `BED_TEMP` and `EXTRUDER_TEMP`, runs these steps:

1. Starts heating the bed. The nozzle heater is left alone.
2. Homes X and Y only, and moves the toolhead behind the bed, over the
   brush. It waits there for the bed.
3. Heats the nozzle to 200 °C, retracts 4 mm, and waits 8 seconds.
4. Homes Z, with the nozzle hot.
5. Measures the bed height next to the brush, without contact.
6. Cleans the nozzle: one pass through the silicone brush, then wipes
   on the steel strip while the nozzle cools to 150 °C.
7. Levels the gantry and homes Z again.
8. Taps the bed three times at the center and makes the contact point
   Z=0.
9. Scans a bed mesh over the area of the print only.
10. Heats the nozzle to printing temperature next to the print, primes,
    and draws a purge line.

The order of the first steps is deliberate. The nozzle arrives with
plastic from the previous print on it, and it must not be brought near
the bed in that state: cold, the remnant is pressed into the plate;
hot, it is squashed up around the nozzle where the brush cannot reach
it. So it is softened behind the bed first, and only then does the
nozzle approach the bed for homing.

Step 5 exists because the gantry is not level yet at that point. The
wipe height is taken from a measurement beside the brush, so a tilted
gantry does not change how deep the nozzle goes.

During step 2 the Z axis is not homed yet, so the toolhead travels to
the back at whatever height it was left at, plus 5 mm. The bed must
be clear of the previous print.

## 8.2 Before the first print

`CLEAN_NOZZLE` runs the cleaning by itself, in the same order as
`START_PRINT`: it homes X and Y, softens the nozzle behind the bed,
homes Z, measures the bed height beside the brush, wipes, and homes Z
again. The printer does not need to be homed first. The bed must be
clear, as at a print start.

Check the wipe path first, without touching anything. This runs the
wipes 4.5 mm higher than normal; it heats the nozzle, so it takes a
few minutes:

```
CLEAN_NOZZLE BRUSH_Z=3
```

The nozzle must travel over the brush and then over the steel strip,
clear of the frame and the bed edge. Then run it for real and watch
the first descent:

```
CLEAN_NOZZLE
```

## 8.3 Settings

At the top of `macros.cfg`:

| Setting | Default | Meaning |
|---|---|---|
| `variable_wipe_temp` | 200 | Nozzle temperature for the brush pass |
| `variable_tap_temp` | 150 | Nozzle temperature for the tap |
| `variable_clean_retract` | 4 | Retraction before wiping, in mm |
| `variable_end_retract` | 6 | Retraction at the end of a print, in mm |
| `variable_brush_z` | -1.5 | Brush pass height relative to the bed |
| `variable_pad_z` | -0.8 | Steel strip wipe height |
| `variable_mesh_method` | `rapid_scan` | Mesh method |

**`variable_pad_z` needs tuning on your printer.** The steel strip has
no give, and a value that is too deep presses the hot nozzle onto
steel. The default, -0.8, is the value that worked on the one printer
this guide comes from. Nothing says it suits yours, and using it
unchanged is at your own risk.

The cautious way: set it to `0` before your first print, then watch
the strip wipes at real print starts and lower it by 0.2 at a time
until the nozzle just brushes the strip. If it ever presses, raise it.
Do not tune it on a cold printer: the reference it is measured from
shifts a little when everything is hot, and a value that looks right
cold is too deep hot.

**The brush gets one pass only**, at full temperature. Passing a
cooler nozzle carrying half-set plastic through it tears the silicone
pegs.

**`variable_end_retract`** limits how much plastic hardens on the
nozzle after a print. Keep it well under 8 mm: pulling molten filament
too far up can jam the hotend. The purge prime accounts for both
retractions.

## 8.4 OrcaSlicer

Create a separate printer profile, so the profile for Sovol's firmware
stays usable.

Printer settings, Machine G-code, **Machine start G-code** (replace
everything):

```
START_PRINT EXTRUDER_TEMP=[nozzle_temperature_initial_layer] BED_TEMP=[bed_temperature_initial_layer_single]
```

**Machine end G-code** (replace everything):

```
END_PRINT
```

Process settings, Others, G-code output: enable **Label objects** and
**Exclude objects**. The adaptive mesh and the purge line use the
object outlines. Without them the mesh covers the whole bed and the
purge line goes to the front left corner.

Printer settings, Basic information: disable **Auxiliary part cooling
fan** if it is enabled. With native fans, Klipper would treat that
fan's commands as part cooling commands.

## 8.5 Cura (not tested)

Start G-code:

```
START_PRINT EXTRUDER_TEMP={material_print_temperature_layer_0} BED_TEMP={material_bed_temperature_layer_0}
```

End G-code:

```
END_PRINT
```

Cura does not label objects itself. Moonraker can add the labels when
a file is uploaded; in `moonraker.conf`:

```
[file_manager]
enable_object_processing: True
```

None of this was run. Only OrcaSlicer was used.

## 8.6 Timelapse

On the **printer**:

```
cd ~ && git clone https://github.com/mainsail-crew/moonraker-timelapse.git
```

```
cd ~/moonraker-timelapse && make install
```

Accept its offer to install `ffmpeg`. Add to `moonraker.conf`:

```
[timelapse]
output_path: ~/printer_data/timelapse/
frame_path: /tmp/timelapse/printer

[update_manager timelapse]
type: git_repo
primary_branch: main
path: ~/moonraker-timelapse
origin: https://github.com/mainsail-crew/moonraker-timelapse.git
managed_services: klipper moonraker
```

In `printer.cfg`, remove the `#` in front of `[include timelapse.cfg]`.
Restart Moonraker and Klipper. In the slicer, add
`TIMELAPSE_TAKE_FRAME` to the G-code run before each layer change, and
enable the feature on Mainsail's Timelapse page.

Tested with a print: the frames were captured and the video was
rendered at the end.
