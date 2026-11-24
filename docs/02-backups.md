# 2. Backups

Three things are backed up while the printer still runs Sovol's
system: the files on the host, the firmware of both boards, and the
whole eMMC.

## 2.1 Host files

On the **PC**. This streams Sovol's home directory, which includes the
configuration and Sovol's Klipper tree, without using space on the
printer:

```
ssh sovol@PRINTER_ADDRESS "tar --create --gzip --file=- --exclude=/home/sovol/printer_data/gcodes --exclude=/home/sovol/printer_data/timelapse /home/sovol" > sv08-sovol-home.tar.gz
```

```
tar --list --gzip --file=sv08-sovol-home.tar.gz | wc --lines
```

Keep a readable copy of `printer.cfg` at hand: chapter 6 reuses values
from it.

## 2.2 Firmware of the two boards

The two boards do not have the same chip:

| Board | Flash size | Read size |
|---|---|---|
| Mainboard | 512 KiB | `0x80000` |
| Toolhead | 128 KiB | `0x20000` |

Reading 512 KiB from the toolhead does not give a valid backup.

**Wiring.** Printer switched off. Both boards have a four-pin header
labelled `3V3 IO CK G`. Connect it to the ST-Link:

| Board | ST-Link |
|---|---|
| 3V3 | 3.3V |
| IO | SWDIO |
| CK | SWCLK |
| G | GND |

Check the pin order printed on your own adapter; clones differ. The
ST-Link powers the board.

This guide has no pictures of its own. For photos showing where the
header is on each board, the pinout, and the ST-Link wiring, see
[step 6 of Rappetor's guide](https://github.com/Rappetor/Sovol-SV08-Mainline#step-6---stock-firmware-backup). The
same section shows how to read the firmware on Windows with
STM32CubeProgrammer; if you do that, use the read sizes from the table
above, because the two boards differ.

**Tool.** Use OpenOCD. With these boards the `stlink` tools
(`st-flash` 1.8.0 and `stlink-gui`) connected only intermittently,
most of all on the toolhead, while OpenOCD connected every time with
the same adapter and wiring.

On the **PC**:

```
sudo apt-get --yes install openocd
```

Check the connection first. This reads nothing and writes nothing:

```
openocd --file interface/stlink.cfg --file target/stm32f1x.cfg --command "adapter speed 100" --command "init" --command "reset halt" --command "flash probe 0" --command "shutdown"
```

A good connection reports `Target voltage` around 3.2, a `Cortex-M3`
processor, and the flash size: 512 KiB on the mainboard, 128 KiB on
the toolhead.

Read the mainboard twice:

```
openocd --file interface/stlink.cfg --file target/stm32f1x.cfg --command "adapter speed 100" --command "init" --command "reset halt" --command "dump_image mainboard-stock-a.bin 0x08000000 0x80000" --command "shutdown"
```

```
openocd --file interface/stlink.cfg --file target/stm32f1x.cfg --command "adapter speed 100" --command "init" --command "reset halt" --command "dump_image mainboard-stock-b.bin 0x08000000 0x80000" --command "shutdown"
```

Move the ST-Link to the toolhead and read it twice:

```
openocd --file interface/stlink.cfg --file target/stm32f1x.cfg --command "adapter speed 100" --command "init" --command "reset halt" --command "dump_image toolhead-stock-a.bin 0x08000000 0x20000" --command "shutdown"
```

```
openocd --file interface/stlink.cfg --file target/stm32f1x.cfg --command "adapter speed 100" --command "init" --command "reset halt" --command "dump_image toolhead-stock-b.bin 0x08000000 0x20000" --command "shutdown"
```

Verify:

```
ls -l mainboard-stock-a.bin mainboard-stock-b.bin toolhead-stock-a.bin toolhead-stock-b.bin
```

```
sha256sum mainboard-stock-a.bin mainboard-stock-b.bin toolhead-stock-a.bin toolhead-stock-b.bin
```

The mainboard files must be 524288 bytes and the toolhead files 131072
bytes. The two reads of each board must have the same hash, and the
two boards must differ.

> Note on what was verified: on the printer this guide comes from, the
> dumps were read with `stlink-gui`, after many connection attempts,
> and checked by hash in the same way. OpenOCD was adopted afterwards
> and used for probing and for writing. The `dump_image` commands above
> are the equivalent read and were not run in exactly this form.

If Katapult was installed before the eddy kit, it is gone: installing
the kit's firmware overwrites it.

## 2.3 The eMMC

Shut the printer down, move the eMMC module to the USB reader, and
plug it into the **PC**.

Identify the device. Run this before and after plugging the reader in,
and note the name that appears (for example `sda`):

```
lsblk --output NAME,SIZE,MODEL,TRAN,MOUNTPOINTS
```

The commands below use `/dev/sdX`. Replace `sdX` with your device, and
check its size matches the module: a wrong name here reads, and later
overwrites, another disk.

Unmount whatever the desktop mounted, and image the module:

```
sudo umount /dev/sdX1 /dev/sdX2
```

```
sudo dd if=/dev/sdX bs=4M status=progress | gzip --fast > sv08-sovol-emmc.img.gz
```

Verify the image against the module. The two hashes must be identical:

```
sudo sha256sum /dev/sdX
```

```
gzip --decompress --stdout sv08-sovol-emmc.img.gz | sha256sum
```

Store the three backups (home archive, four firmware files, eMMC
image) somewhere other than this PC as well.
