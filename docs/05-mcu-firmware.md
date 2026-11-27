# 5. Firmware on the two boards

Both boards get the Katapult bootloader, written once with the
ST-Link, and then Klipper, written over USB. From then on firmware
updates need no ST-Link.

After Katapult is written and until Klipper is flashed, the printer
is silent at power-on: no fans, no light, and the knob LCD stays on
its splash picture. That is normal.

## 5.1 Build Katapult

On the **printer**:

```
cd ~ && git clone https://github.com/Arksine/katapult
```

```
cd ~/katapult && make menuconfig
```

Settings:

| Option | Value |
|---|---|
| Micro-controller Architecture | STMicroelectronics STM32 |
| Processor model | STM32F103 |
| Only 10KiB of RAM | off |
| Disable SWD at startup | **off** |
| Build Katapult deployment application | Do not build |
| Clock Reference | 8 MHz crystal |
| Communication interface | USB (on PA11/PA12) |
| Application start offset | 8KiB offset |
| USB ids | defaults |
| Build Optimization Override | default |
| GPIO pins to set on bootloader entry | empty |
| Support bootloader entry on rapid double click of reset button | **off** |
| Enable bootloader entry on button (or gpio) state | off |
| Enable Status LED | off |

Leaving SWD enabled keeps the ST-Link usable for recovery. The double
click option is on by default in current Katapult; with it, two quick
resets would leave a board waiting in the bootloader.

Press `Q`, save, and build:

```
make clean && make
```

## 5.2 Make full-size images

Katapult starts whatever sits after it in the flash unless that area
is blank, and right now it holds remains of Sovol's firmware. Writing
an image that is Katapult followed by blank bytes for the whole chip
erases those remains, and makes the result verifiable.

```
cd ~/katapult/out && tr "\000" "\377" < /dev/zero | head --bytes=524288 > katapult-mainboard-512k.bin && dd if=katapult.bin of=katapult-mainboard-512k.bin conv=notrunc
```

```
cd ~/katapult/out && tr "\000" "\377" < /dev/zero | head --bytes=131072 > katapult-toolhead-128k.bin && dd if=katapult.bin of=katapult-toolhead-128k.bin conv=notrunc
```

```
ls -l ~/katapult/out/katapult-mainboard-512k.bin ~/katapult/out/katapult-toolhead-128k.bin && sha256sum ~/katapult/out/katapult-mainboard-512k.bin ~/katapult/out/katapult-toolhead-128k.bin
```

Sizes must be 524288 and 131072 bytes. Copy both to the **PC** and
compare the hashes there with the ones just printed:

```
scp sovol@PRINTER_ADDRESS:/home/sovol/katapult/out/katapult-mainboard-512k.bin sovol@PRINTER_ADDRESS:/home/sovol/katapult/out/katapult-toolhead-128k.bin .
```

```
sha256sum katapult-mainboard-512k.bin katapult-toolhead-128k.bin
```

## 5.3 Write Katapult with the ST-Link

This is the point of no return for each board: after it, the board no
longer runs Sovol's firmware. Your dumps from chapter 2 are the way
back.

The commands below are for Linux. On Windows, write the same two
image files with STM32CubeProgrammer as shown, with screenshots, in
[step 7 of Rappetor's guide](https://github.com/Rappetor/Sovol-SV08-Mainline#step-7---flash-katapult-bootloader):
`katapult-mainboard-512k.bin` to the mainboard and
`katapult-toolhead-128k.bin` to the toolhead, both at address
`0x08000000`. That was not tested here.

Shut the printer down and switch it off:

```
sudo poweroff
```

Wire the ST-Link to the **mainboard** as in chapter 2. On the **PC**:

```
openocd --file interface/stlink.cfg --file target/stm32f1x.cfg --command "adapter speed 100" --command "init" --command "reset halt" --command "flash write_image erase katapult-mainboard-512k.bin 0x08000000 bin" --command "verify_image katapult-mainboard-512k.bin 0x08000000 bin" --command "shutdown"
```

Move the ST-Link to the **toolhead**:

```
openocd --file interface/stlink.cfg --file target/stm32f1x.cfg --command "adapter speed 100" --command "init" --command "reset halt" --command "flash write_image erase katapult-toolhead-128k.bin 0x08000000 bin" --command "verify_image katapult-toolhead-128k.bin 0x08000000 bin" --command "shutdown"
```

Each must end with a `wrote` line and a `verified` line for the full
size (524288 or 131072 bytes). If a write is interrupted, run it
again; nothing is lost.

> Note on what was verified: the toolhead was written with exactly the
> command above. The mainboard was written with `stlink-gui` and
> checked by reading it back and comparing hashes. The mainboard
> command above is the same operation with the tool that proved
> reliable.

Remove the ST-Link and all its wires.

## 5.4 Tell the two boards apart

Switch the printer on, log in, and on the **printer**:

```
ls -l /dev/serial/by-id/
```

```
ls -l /dev/serial/by-path/
```

The first listing shows two entries starting with
`usb-katapult_stm32f103xe_`, each with its own serial number. The
second shows which USB port each device is on, and the ports are fixed
by the printer's wiring:

| `by-path` contains | Board | Klipper name |
|---|---|---|
| `platform-5200400` | Mainboard | `mcu` |
| `platform-5101400` | Toolhead | `extra_mcu` |

Match the `ttyACM` numbers between the two listings and write down
which serial is `MAINBOARD_SERIAL` and which is `TOOLHEAD_SERIAL`.
Every command and file from here on depends on getting this right.

## 5.5 Klipper for the mainboard

On the **printer**:

```
sudo systemctl stop klipper
```

```
cd ~/klipper && make clean KCONFIG_CONFIG=config.mainboard && make menuconfig KCONFIG_CONFIG=config.mainboard
```

| Option | Value |
|---|---|
| Enable extra low-level configuration options | on |
| Micro-controller Architecture | STMicroelectronics STM32 |
| Processor model | STM32F103 |
| Only 10KiB of RAM | off |
| Disable SWD at startup | off |
| Bootloader offset | 8KiB bootloader |
| Clock Reference | 8 MHz crystal |
| Communication interface | USB (on PA11/PA12) |
| USB ids | defaults |
| GPIO pins to set at micro-controller startup | `PA1,PA3` |

`PA1,PA3` switches the mainboard fan and the light on at power-up.

```
make KCONFIG_CONFIG=config.mainboard --jobs=4
```

```
~/klippy-env/bin/python ~/katapult/scripts/flashtool.py --firmware ~/klipper/out/klipper.bin --device /dev/serial/by-id/usb-katapult_stm32f103xe_MAINBOARD_SERIAL-if00
```

It must end with `Programming Complete`.

## 5.6 Klipper for the toolhead

Same settings, except the last line:

```
cd ~/klipper && make clean KCONFIG_CONFIG=config.toolhead && make menuconfig KCONFIG_CONFIG=config.toolhead
```

| Option | Value |
|---|---|
| GPIO pins to set at micro-controller startup | `PA6` |

`PA6` runs the hotend fan from power-up until Klipper takes over.

```
make KCONFIG_CONFIG=config.toolhead --jobs=4
```

```
~/klippy-env/bin/python ~/katapult/scripts/flashtool.py --firmware ~/klipper/out/klipper.bin --device /dev/serial/by-id/usb-katapult_stm32f103xe_TOOLHEAD_SERIAL-if00
```

Check:

```
ls -l /dev/serial/by-id/
```

Both entries now start with `usb-Klipper_stm32f103xe_`.

## 5.7 Later firmware updates

When Klipper is updated on the host, the boards can be rebuilt and
reflashed over USB with the same two named configurations
(`config.mainboard`, `config.toolhead`), without the ST-Link.
[Chapter 13](13-updating.md) has the procedure.
