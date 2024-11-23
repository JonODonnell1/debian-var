#!/bin/bash -ex
time \
    (
        (   sudo apt-get reinstall binfmt-support >> /dev/null     # fix debootstral format not recignized error
            cd src/kernel; sudo make distclean; cd ../..           # force new kernel version string for uname
            cd src/uboot; sudo make distclean; cd ../..            # force new uboot version string
            sudo rm -rf rootfs output tmp                          # clean up before build
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c bootloader
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c kernel
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c modules
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c kernelheaders
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c rootfs
            sudo custom/build.sh
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c rtar
            RTAR="ma6-`date +%Y%m%d-%H%M`.img"
            if [ -z $MA6_IMAGE_DIR ]; then MA6_IMAGE_DIR="."; fi
            dd if=/dev/zero of=$MA6_IMAGE_DIR/$RTAR bs=1M count=7440
            LOOP=`sudo losetup -Pf --show $MA6_IMAGE_DIR/$RTAR`
            sudo MACHINE=imx8mp-var-dart ./var_make_debian.sh -c sdcard -d ${LOOP}
            sudo losetup -d ${LOOP}
        )   
    ) |& tee build.log
