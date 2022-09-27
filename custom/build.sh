#!/bin/sh -e
cd `dirname $0`
CC=`realpath ../toolchain/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-gcc`
cd src
$CC i2cprog.c -o ../bin/i2cprog
$CC interleave.c -o ../bin/interleave
$CC SigGen.c pink.c -lm -o ../bin/SigGen
$CC RMS.c -lm -o ../bin/RMS
cd ..

install -m 755 bin/* ../rootfs/usr/bin
install -m 755 root/* ../rootfs/root
install -m 755 root/.bashrc ../rootfs/root
install -m 644 pulseaudio/daemon.conf ../rootfs/etc/pulse
install -m 644 pulseaudio/default.pa  ../rootfs/etc/pulse
install -m 644 pulseaudio/system.pa   ../rootfs/etc/pulse
install -m 644 pulseaudio/m5pro*.conf ../rootfs/usr/share/pulseaudio/alsa-mixer/profile-sets
install -m 755 systemd/scripts/*      ../rootfs/usr/lib/systemd/scripts
install -m 644 systemd/*.service      ../rootfs/usr/lib/systemd/system
install -m 755 -d ../rootfs/etc/systemd/system/multi-user.target.wants
install -m 755 -d ../rootfs/etc/systemd/system/shutdown.target.wants
ln -s -f /usr/lib/systemd/system/m5pro-start.service    ../rootfs/etc/systemd/system/multi-user.target.wants/m5pro-start.service
ln -s -f /usr/lib/systemd/system/m5pro-shutdown.service ../rootfs/etc/systemd/system/shutdown.target.wants/m5pro-shutdown.service

#cleanup old
rm -f ../rootfs/etc/rc5.d/S99m5pro
rm -f ../rootfs/etc/init.d/m5pro.sh
