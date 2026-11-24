# 10. Going back to Sovol's firmware

Going back needs two things, because both the host and the boards were
changed.

**None of this was exercised.** The backups were made and verified;
the restore was not needed. The commands are the reverse of ones that
were run.

## 10.1 The boards

Printer off, ST-Link wired as in chapter 2. On the **PC**, write each
board's own dump back.

Mainboard:

```
openocd --file interface/stlink.cfg --file target/stm32f1x.cfg --command "adapter speed 100" --command "init" --command "reset halt" --command "flash write_image erase mainboard-stock-a.bin 0x08000000 bin" --command "verify_image mainboard-stock-a.bin 0x08000000 bin" --command "shutdown"
```

Toolhead:

```
openocd --file interface/stlink.cfg --file target/stm32f1x.cfg --command "adapter speed 100" --command "init" --command "reset halt" --command "flash write_image erase toolhead-stock-a.bin 0x08000000 bin" --command "verify_image toolhead-stock-a.bin 0x08000000 bin" --command "shutdown"
```

Do not mix the two files up: the mainboard file is 524288 bytes and
the toolhead file 131072 bytes.

## 10.2 The host

If you kept the original eMMC module untouched, fit it.

Otherwise restore the image from chapter 2 onto a module, on the
**PC**, with `sdX` identified as in chapter 2:

```
sudo umount /dev/sdX1 /dev/sdX2
```

```
gzip --decompress --stdout sv08-sovol-emmc.img.gz | sudo dd of=/dev/sdX bs=4M conv=fsync status=progress
```

The image is as large as the module it was taken from, so the target
must be at least that size.

## 10.3 Slicer

Switch back to the printer profile with Sovol's start and end G-code.
