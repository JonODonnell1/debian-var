#!/bin/bash -ex
#time                                                                                         \
#    (                                                                                        \
#        (   sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c kernel                   && \
#            sudo cp output/Image.gz rootfs/boot/Image.gz                                  && \
#            sudo rm -r rootfs/boot/*.dtb                                                  && \
#            sudo cp output/*.dtb rootfs/boot                                              && \
#            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c rtar                     && \ 
#            dd if=/dev/zero of=/mnt/shared/imx8mp-var-dart-debian-sd.img bs=1M count=3720 && \
#            LOOP=`sudo losetup -Pf --show /mnt/shared/imx8mp-var-dart-debian-sd.img`      && \
#            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c sdcard -d ${LOOP};          \
#        )   |& tee build.log;                                                                \
#    )
sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c kernel                            |& tee build.log
sudo cp output/Image.gz rootfs/boot/Image.gz
sudo rm -r rootfs/boot/*.dtb
sudo cp output/*.dtb rootfs/boot
sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c rtar                              |& tee -a build.log
dd if=/dev/zero of=/mnt/shared/imx8mp-var-dart-debian-sd.img bs=1M count=3720
readonly LOOPDEV="`sudo losetup -Pf --show /mnt/shared/imx8mp-var-dart-debian-sd.img`"
sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c sdcard -d "${LOOPDEV}"            |& tee -a build.log
sudo losetup -d "${LOOPDEV}"
