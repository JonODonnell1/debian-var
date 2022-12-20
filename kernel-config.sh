#!/bin/bash
cd src/kernel
make ARCH=arm64 imx8_var_defconfig
make ARCH=arm64 xconfig
make ARCH=arm64 savedefconfig
cp defconfig arch/arm64/configs/imx8_var_defconfig
