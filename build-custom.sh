#!/bin/bash -ex
time \
    ( \
        (   sudo custom/build.sh                                                          && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c rtar                     && \
            dd if=/dev/zero of=/mnt/shared/imx8mp-var-dart-debian-sd.img bs=1M count=3720 && \
            LOOP=`sudo losetup -Pf --show /mnt/shared/imx8mp-var-dart-debian-sd.img`      && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c sdcard -d ${LOOP}        && \
            sudo losetup -d ${LOOP};                                                         \
        )   |& tee build.log; \
    )
