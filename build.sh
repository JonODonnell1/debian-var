!#/bin/sh -e
time \
    ( \
        (   sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c bootloader               && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c kernel                   && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c modules                  && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c kernelheaders            && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c rootfs                   && \
            dd if=/dev/zero of=/mnt/shared/imx8mp-var-dart-debian-sd.img bs=1M count=3720 && \
            LOOP=`sudo losetup -Pf --show /mnt/shared/imx8mp-var-dart-debian-sd.img`      && \
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c sdcard -d ${LOOP}        && \
            sudo losetup -d ${LOOP};                                                         \
        )   |& tee build.log; \
    )
