#!/bin/sh -e
cd `dirname $0`
CC=`realpath ../toolchain/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-gcc`
CPP=`realpath ../toolchain/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-g++`
cd src
$CC i2cprog.c -o ../bin/i2cprog
$CC interleave.c -o ../bin/interleave
$CC deinterleave.c -o ../bin/deinterleave
$CC SigGen.c pink.c -lm -o ../bin/SigGen
$CC RMS.c -lm -o ../bin/RMS
$CPP THDn.cpp FFTWindow.cpp -lm -mcpu=cortex-a53 -mtune=cortex-a53 -o ../bin/THDn
$CPP FFT.cpp FFTWindow.cpp -lm -mcpu=cortex-a53 -mtune=cortex-a53 -o ../bin/FFT
cd ..

install -m 755 bin/*                                  ../rootfs/usr/bin
install -m 755 root/*                                 ../rootfs/root
install -m 755 root/.bashrc                           ../rootfs/root
install -m 644 pulseaudio/daemon.conf                 ../rootfs/etc/pulse
install -m 644 pulseaudio/default.pa                  ../rootfs/etc/pulse
install -m 644 pulseaudio/system.pa                   ../rootfs/etc/pulse
install -m 644 pulseaudio/ma6*.conf                   ../rootfs/usr/share/pulseaudio/alsa-mixer/profile-sets
install -m 755 systemd/scripts/ma6.sh                 ../rootfs/usr/lib/systemd/scripts
install -m 644 systemd/ma6-start.service              ../rootfs/usr/lib/systemd/system
install -m 644 systemd/ma6-shutdown.service           ../rootfs/usr/lib/systemd/system
install -m 755 -d                                     ../rootfs/etc/systemd/system/multi-user.target.wants
install -m 755 -d                                     ../rootfs/etc/systemd/system/shutdown.target.wants
ln -s -f /usr/lib/systemd/system/ma6-start.service    ../rootfs/etc/systemd/system/multi-user.target.wants/ma6-start.service
ln -s -f /usr/lib/systemd/system/ma6-shutdown.service ../rootfs/etc/systemd/system/shutdown.target.wants/ma6-shutdown.service
install -m 644 images/*                               ../rootfs/usr/share/images/desktop-base

#cleanup old
rm -f ../rootfs/etc/rc5.d/S99ma6
rm -f ../rootfs/etc/init.d/ma6.sh
