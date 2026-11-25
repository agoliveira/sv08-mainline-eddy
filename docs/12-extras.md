# 12. Extras

Optional additions. The printer works as described without them, and
they are not part of the files in `config/`.

## 12.1 Beeper signals

The knob LCD has a beeper, and the base configuration only defines a
single short `BEEP`. This extra turns it into signals:

| Event | Sound |
|---|---|
| Start sequence done, first layer about to begin | 1 beep |
| Print finished | 3 short beeps |
| Filament runout | 5 long beeps, repeated every 30 seconds until the print is resumed or cancelled |
| Filament change requested by the G-code (`M600`) | The same repeating alarm |

`BEEP` also becomes general, for use in your own macros or from the
console:

```
BEEP COUNT=3 MS=150 PAUSE=150
```

Times are in milliseconds, with a minimum of 100.

**Install.** The changes touch several places in `macros.cfg` and one
in `printer.cfg`, so they are applied by a script,
[`extras/sv08-beeper-patch.py`](../extras/sv08-beeper-patch.py). It
edits the two files in place, keeps a copy of each next to the
original, and changes nothing if the files are not as it expects (for
example if they were already patched or heavily modified).

On the **PC**, from the repository directory:

```
scp extras/sv08-beeper-patch.py sovol@PRINTER_ADDRESS:/home/sovol/
```

On the **printer**:

```
python3 ~/sv08-beeper-patch.py
```

Then do a Firmware Restart in Mainsail and test with the `BEEP`
command above.

**Silence.** `variable_beeper_enabled` at the top of `macros.cfg` is a
master switch. Set it to `False` and restart to mute every signal.

**Volume.** The beeper generates its own tone at one fixed loudness,
so the volume cannot be raised in software. If it is quiet, open the
knob LCD's case and look at the buzzer: on the printer this was
written on, the factory seal was still stuck over its sound hole.
Peeling it off made the beeper much louder.

There is no signal on cancel or on errors. After a Klipper shutdown
nothing can drive the beeper.

## 12.2 Temperature-controlled mainboard fan

In the base configuration the mainboard fan is on while a heater or
the X/Y motors are active, and off otherwise. This variant, adapted
from [Rappetor's configuration](https://github.com/Rappetor/Sovol-SV08-Mainline),
regulates its speed on the host processor's temperature instead.

In `printer.cfg`, replace the whole `[controller_fan mcu_fan]` section
with:

```
[temperature_fan mcu_fan]
pin: PA1
hardware_pwm: True
kick_start_time: 0.5
max_power: 1.0
sensor_type: temperature_host
min_temp: 0
max_temp: 90
target_temp: 60
min_speed: 0.3
max_speed: 1.0
control: pid
pid_Kp: 2.0
pid_Ki: 5.0
pid_Kd: 0.5
pid_deriv_time: 2.0
```

and delete the `[temperature_sensor Host_temp]` section, because the
fan's own row in Mainsail now shows that temperature.

Things to know:

- The fan never stops: `min_speed` keeps it at 30% whenever the
  printer is on. That floor is deliberate. The same fan cools the
  stepper drivers, which have no temperature sensor, so regulating on
  the host temperature alone could leave them without airflow.
- With a target of 60 °C, the fan stays at its floor most of the time
  and speeds up only when the host gets hot.
- In Mainsail the fan's row is named after the fan (`Mcu Fan`) but
  shows the host processor's temperature. `Mcu Temp` is a different
  chip, the mainboard's micro-controller.
- Rappetor's notes say this does not work with a Noctua 24 V 4010
  fan, and suggest `control: watermark` in that case.

Treat the target and the minimum speed as starting values. They were
run for a short time with the stock fan, and then with the larger fan
described below.

**A larger fan.** The stock fan is small and noisy. A printed mount,
[Sovol SV08 Electronics 8010 Fan Mount](https://www.printables.com/model/1104389-sovol-sv08-elecronics-8010-fan-mount),
replaces the metal bottom plate of the electronics bay and holds an
80 mm fan blowing straight onto the mainboard. With a two-wire 24 V
8010 fan on the stock fan's connector and the section above unchanged,
the fan idles at its 30% floor with the host at about 50 °C, and is
much quieter than the stock one.

Before choosing this, consider:

- The fan takes its air from under the printer, so the printer needs
  feet tall enough to leave that space open.
- The electronics bay is no longer closed from below. A fan grill
  keeps fingers, cables and debris out of the blades.
- Keep the metal plate and its screws to be able to go back.
