#!/bin/bash -ex
time \
    ( \
        (   sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c bootloader               && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c kernel                   && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c modules                  && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c kernelheaders            && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c rootfs                   && \
            sudo custom/build.sh                                                          && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c rtar                     && \
            RTAR="m5pro-`date +%Y%m%d-%H%M`.img"                                          && \
            dd if=/dev/zero of=/mnt/shared/$RTAR bs=1M count=7440                         && \
            LOOP=`sudo losetup -Pf --show /mnt/shared/$RTAR`                              && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c sdcard -d ${LOOP}        && \
            sudo losetup -d ${LOOP};                                                         \
        )   |& tee build.log; \
    )
