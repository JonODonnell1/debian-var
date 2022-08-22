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
install -m 755 init.d/m5pro.sh ../rootfs/etc/init.d
install -m 755 root/* ../rootfs/root
rm -f ../rootfs/etc/rc5.d/S99m5pro
ln -s ../init.d/m5pro.sh ../rootfs/etc/rc5.d/S99m5pro
