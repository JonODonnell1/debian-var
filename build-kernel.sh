#!/bin/bash -ex
time \
    (
        (   cd src/kernel; sudo make distclean; cd ../..     # force new kernel version string for uname
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c bootloader
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c kernel
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c modules
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c kernelheaders
            sudo cp output/Image.gz rootfs/boot/Image.gz
            sudo rm -r rootfs/boot/*.dtb
            sudo cp output/*.dtb rootfs/boot
            sudo custom/build.sh
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c rtar
            RTAR="m5pro-`date +%Y%m%d-%H%M`.img"
            if [ -z $M5PRO_IMAGE_DIR ]; then M5PRO_IMAGE_DIR="."; fi
            dd if=/dev/zero of=$M5PRO_IMAGE_DIR/$RTAR bs=1M count=7440
            LOOP=`sudo losetup -Pf --show $M5PRO_IMAGE_DIR/$RTAR`
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c sdcard -d ${LOOP}
            sudo losetup -d ${LOOP}
        )   |& tee build.log
    )
