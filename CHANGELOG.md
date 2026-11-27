# Changelog

## 2026-11-27

- New chapter 13, Updating, written from a real update (Klipper
  `v0.14.0-0` to `v0.14.0-1`) with both boards reflashed over USB.
  Section 5.7 now points to it.
- Section 7.4 and troubleshooting: tap only at a stable nozzle
  temperature.
- README: updating is no longer listed as not verified; going back
  after an update is.

## 2026-11-26

- `CLEAN_NOZZLE` runs in the same order as `START_PRINT` (soften
  behind the bed, home Z hot, height reference beside the brush, wipe)
  and ends with the nozzle heater off. Section 8.2 updated.
- Steel strip wipe height: default -0.8, with a caution on tuning it.
- Idle timeout of 30 minutes in place of Sovol's value (about 69 days).
- Chapter 9: run `SHAPER_CALIBRATE` with the heaters off; new section
  9.5 on the damping ratio and on slicer tests that leave their values
  active.
- New sections: 6.5 (copy of the configuration), 8.7 (filament
  tuning). Duration of the start sequence and a note on cancelled
  prints in 8.1. `passwd` in 3.5.
- Troubleshooting: input shaper entries.
- README: updating Klipper is listed as not verified.

## 2026-11-25

- Chapter 12, Extras: beeper signals and a temperature-controlled
  mainboard fan, then the 80 mm fan mount and the buzzer seal.
- Timelapse verified with a print.

## 2026-11-24

- First publication.
- Note that the PC side was done on Linux only, with pointers to
  Rappetor's guide for Windows and for photos.
