#!/bin/bash

. /lib/lsb/init-functions
VERBOSE=yes

verbose=""
[ "$VERBOSE" = yes ] && verbose=-v

retries=4

verbose_log_begin_msg() { [ "$VERBOSE" = no ] || log_begin_msg "$@"; }
verbose_log_end_msg() { [ "$VERBOSE" = no ] || log_end_msg "$@"; }
verbose_log_action_msg() { [ "$VERBOSE" = no ] || log_action_msg "$@"; }
verbose_log_success_msg() { [ "$VERBOSE" = no ] || log_success_msg "$@"; }

pulseaudio_init(){
    verbose_log_begin_msg "M5pro pulseaudio_init"

    i=0
    while [ true ]; do
        i=$(($i+1))

        DUMMY1_CARD=`cat /sys/devices/platform/sound-dummy-1/sound/card?/number`
        DUMMY2_CARD=`cat /sys/devices/platform/sound-dummy-2/sound/card?/number`
        HDMI_CARD=`cat /sys/devices/platform/sound_hdmi/sound/card?/number`

        pactl suspend-source 0
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break;
            fi
        fi
        pactl suspend-sink 0
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break;
            fi
        fi
        pactl load-module module-alsa-card device_id="$DUMMY1_CARD" name="platform-sound-dummy-1" card_name="alsa_card.platform-sound-dummy-1" namereg_fail=false fixed_latency_range=no ignore_dB=no deferred_volume=yes avoid_resampling=no card_properties="module-udev-detect.discovered=1" rate=192000 format=s32le profile_set=m5pro-1.conf
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break;
            fi
        fi

        pactl suspend-source 0
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break;
            fi
        fi
        pactl suspend-sink 0
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break;
            fi
        fi
        pactl load-module module-alsa-card device_id="$DUMMY2_CARD" name="platform-sound-dummy-2" card_name="alsa_card.platform-sound-dummy-2" namereg_fail=false fixed_latency_range=no ignore_dB=no deferred_volume=yes avoid_resampling=no card_properties="module-udev-detect.discovered=1" rate=48000  format=s32le profile_set=m5pro-2.conf
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break;
            fi
        fi

        pactl suspend-source 0
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break;
            fi
        fi
        pactl suspend-sink 0
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break;
            fi
        fi
        pactl load-module module-alsa-card device_id="$HDMI_CARD"   name="audiohdmi"              card_name="alsa_card.audiohdmi"              namereg_fail=false fixed_latency_range=no ignore_dB=no deferred_volume=yes avoid_resampling=no card_properties="module-udev-detect.discovered=1" rate=192000 format=s32le profile_set=m5pro-hdmi-out.conf
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break;
            fi
        else
            # success
            break
        fi
    done

    verbose_log_end_msg 0
}

nvme_init(){
    verbose_log_begin_msg "M5pro nvme_init"
    if [ `df | grep /dev/nvme0n1 | wc -l` -eq 0 ]; then
        if [ ! -c /dev/nvme0 ]; then
            log_action_msg "ERROR: M5Pro NVMe Drive found!"
            exit 1
        fi
        if [ ! -b /dev/nvme0n1 ]; then
            log_action_msg "ERROR: M5Pro NVMe Drive Partitions found!"
            exit 1
        fi
        if [ `blkid | grep nvme | wc -l` -eq 0 ]; then
            verbose_log_action_msg "M5Pro Creating NVMe FS"
            mkfs.ext4 /dev/nvme0n1
        fi
        if [ ! -d /mnt/data ]; then
            verbose_log_action_msg "M5Pro Creating NVMe mount point"
            mkdir -p /mnt/data
            chmod 777 /mnt/data
        fi
        UUID=`blkid -o value /dev/nvme0n1 | head -n1`
        if [ `grep ${UUID} /etc/fstab | wc -l` -eq 0 ]; then
            verbose_log_action_msg "M5Pro Adding NVMe to /etc/fstab"
            echo -e "UUID=${UUID}\t/mnt/data\text4\tdefaults,nofail\t0\t2" >> /etc/fstab
        fi
        mount /dev/nvme0n1 /mnt/data
    fi
    chmod 777 /mnt/data
    verbose_log_end_msg 0
}

gpio_setup_out(){
    name=$1
    value=$2
    verbose_log_begin_msg "M5Pro gpio_setup_out $name $value"
    gpio=`gpiofind $name`
    if [ -z "$gpio" ]; then
        log_action_msg "ERROR: M5Pro Unable to find GPIO '$name'"
        exit 1
    fi
    gpioset $gpio=$value
    verbose_log_end_msg 0
}

gpio_setup_in(){
    name=$1
    verbose_log_begin_msg "M5Pro gpio_setup_in $name $value"
    gpio=`gpiofind $name`
    if [ -z "$gpio" ]; then
        log_action_msg "ERROR: M5Pro Unable to find GPIO '$name'"
        exit 1
    fi
    value=`gpioget $gpio`
    verbose_log_end_msg 0
}

es9820(){
    i2c_bus=$1
    i2c_sync_addr=$2
    i2c_addr=$3

    verbose_log_begin_msg "M5Pro Initializing es9820 on i2c-${i2c_bus} @ ${i2c_sync_addr}/${i2c_addr}..."

    i=0
    while [ true ]; do
        i=$(($i+1))

        i2cprog $i2c_bus $i2c_sync_addr <<____________EOF_i2cprog
            193 0x01  # SEL_SYSCLK_IN = 00 (XTAL)
            194 0x00  # SEL_CLK_DIV = 0 (1x)
____________EOF_i2cprog
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break
            fi
        fi
        sleep 0.5
        i2cprog $i2c_bus $i2c_addr <<____________EOF_i2cprog
            0 0x00  # OUTPUT_SEL = 00 (I2S)
            1 0x33  # ENABLE_ADC_CH and ENABLE_DATA_IN_CH
            2 0x01  # SELECT_ADC_NUM = 1 (192k)
            3 0x00  # SELECT_IADC_NUM = SEL_CLK_DIV
            8 0x00  # MASTER_BCK_DIV1 = 0, MASTER_MODE_ENABLE = 0
            9 0x00  # master mode is disabled
            10 0x05  # TDM_VALID_EDGE = 1, ENABLE_TDM_CLK = 1
            11 0x01  # TDM_CH_NUM = 1 (# of channels = 1 + TDN_CH_NUM = 2)
            12 0x00  # TDM_LINE_SEL_CH1: 00 (GPIO3), TDM_SLOT_SEL_CH1: 0 (slot 0)
            13 0x01  # TDM_LINE_SEL_CH2: 00 (GPIO3), TDM_SLOT_SEL_CH2: 1 (slot 1)
            23 0x0A  # FS_PHASE = 10
            74 0x11  # GPIO1 and GPIO2 set to AUX input (slave mode)
            75 0x02  # GPIO3 set to AUX output
            86 0x03  # GPIO1 and GPIO2 input enabled
            88 0x04  # GPIO3 output enabled
            63 0xBB  # adc ch1 config
            64 0x38
            65 0xBB  # adc ch2 config
            66 0x38
            71 0x0F  # set common mode to 3
            113 0x98  # ADC1_FILTER_SHAPE = Minimum phase slow roll off
            118 0x01
            130 0x98  # ADC2_FILTER_SHAPE = Minimum phase slow roll off
____________EOF_i2cprog
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break
            fi
        else
            # success
            break
        fi
    done
    verbose_log_end_msg 0
}

es9033(){
    i2c_bus=$1
    i2c_sync_addr=$2
    i2c_addr=$3

    verbose_log_begin_msg "M5Pro Initializing es9033 on i2c-${i2c_bus} @ ${i2c_sync_addr}/${i2c_addr}..."

    i=0
    while [ true ]; do
        i=$(($i+1))

        i2cprog $i2c_bus $i2c_sync_addr <<____________EOF_i2cprog
            192 0x03  # GPIO_SDB_SYNC=1 (SYS_CLK provided through GPIO1), and PLL_XLKHV_PHASE=1 (clocks have same phase)
            193 0x81  # BYPASS_PLL=1 and EN_PLL_CLKIN=1
            202 0x40  # PLL REG PDB 1v2=1
____________EOF_i2cprog
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break
            fi
        fi
        sleep 0.1
        i2cprog $i2c_bus $i2c_addr <<____________EOF_i2cprog
            0 0x3E  # SYSTEM_CONFIG AMP_MODE_REG=1
____________EOF_i2cprog
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break
            fi
        else
            # success
            break
        fi
    done

    verbose_log_end_msg 0
}

src4392_out(){
    i2c_bus=$1
    i2c_addr=$2
    mux=$3
    clk_div=$4

    verbose_log_begin_msg "M5Pro Initializing src4392 for output on i2c-${i2c_bus} @ ${i2c_addr}..."

    i=0
    while [ true ]; do
        i=$(($i+1))

        # TODO: Simple DIT.  No SRC/clock divider for now
        i2cprog $i2c_bus $i2c_addr <<____________EOF_i2cprog
            0x7F 0x00  # Register Page 0
            0x01 0x80  #  Reset
            0x03 0x21  #  I2S Port A: Clock Slave, 24 Bit Audio I2S, Output Signal from Receiver (NOT from SRC) (??? ref has 0x20 ???)
            0x04 0x00  #  I2S Port A: MCLK source = MCLK, MCLK Freq = 128x LRCLK
            0x05 0x01  #  I2S Port B: Clock Slave, 24 Bit Audio I2S, Loopback for now
            0x06 0x04  #  I2S Port B: MCLK source = RXCKI, MCLK freq = 128x LRCLK (TODO: divider needs to be adjustable)
            0x07 0x00  #  Clock Start Output; Transmitter Source=Port A, Transmitter MCLK DIvider = FPGA CLK/128, TXCLK=MCLK
            0x09 0x00  #  Transmitter Channel State static
            0x0D 0x08  #  Receover Input = RX1, Ref Clk=MCLK
            0x0E 0x00  #  Mute if no CLK
            0x0F 0x22  #  24.576MHz / 2 (P) * 8.0000 (J.D) = 98.304MHz (P=2, J=8, D=0)
            0x10 0x00  # 
            0x11 0x00  #
            0x2D 0x02  #  SRC Input = DIR, SRCCLK=MCLK, SRC Mute
            0x01 0x3F  #  All on
____________EOF_i2cprog
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break
            fi
        else
            # success
            break
        fi
    done

    verbose_log_end_msg 0
}

src4392_in(){
    i2c_bus=$1
    i2c_addr=$2

    verbose_log_begin_msg "M5Pro Initializing src4392 for input on i2c-${i2c_bus} @ ${i2c_addr}..."

    i=0
    while [ true ]; do
        i=$(($i+1))

        i2cprog $i2c_bus $i2c_addr <<____________EOF_i2cprog
            0x7F 0x00  # Register Page 0
            0x01 0x80  #  Reset
            0x03 0x31  #  I2S Port A: Clock Slave (0x00), 24 Bit Audio I2S (0x01), Output signal from SRC (0x30), Un-Mute (0x00)
            0x04 0x00  #  I2S Port A: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            0x05 0x41  #  I2S Port B: Clock Slave (0x00), 24 Bit Audio I2S (0x01), Output signal Port B (0x00), Mute (0x40) -- Inactive, Does Not Matter
            0x06 0x00  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00) -- Does Not Matter
            0x07 0x00  #  Data slip (0x00), V=1 (0x00), BLSM Input (0x00), TXIS Port A (0x00), TXDIV 128 (0x00), TXCLK=MCLK (0x00)
            0x08 0x07  #  TXOFF (0x01), TXMUTE (0x02), AESOFF (0x04), TXBTD (0x00), LDMUX AES3 (0x00), AEXMUX AES3 (0x00), BYPMUX=RX1 (0x00)
            0x09 0x00  #  TXCUS (0x00), VALSEL (0x00)
            0x0D 0x08  #  RXMUX=RX1 (0x00), RXCLK=MCLK (0x08), RA/UA transfer enabled (0x00)
            0x0E 0x08  #  RXCKOE disabled (0x00), RXCKO Passthrough (0x00), RXAMLL Enabled (0x08), PLL2 Stop on Loss of lock (0x00)
            0x0F 0x22  #  24.576MHz / 2 (P) * 8.0000 (J.D) = 98.304MHz (P=2, J=8, D=0)
            0x10 0x00  #
            0x11 0x00  #
            0x2D 0x02  #  Input from DIR (0x02), SRCCLK MCLK (0x00), Unmuted (0x00), TRACK Disabled (0x00)
            0x2E 0x00  #  IGRP 64 (0x00), Decimation Filter (0x00), De-emphasis Disabled (0x00), AUTODEM disabled (0x00)
            0x2F 0x00  #  OWL 24 (0x00)
            0x30 0x00  #  0dB Left attenuation 
            0x31 0x00  #  0dB Right attenuation 
            0x01 0x3F  #  All on
____________EOF_i2cprog
        if [ $? -ne 0 ]; then
            if [ $i -le $retries ]; then
                echo "Retrying..."
                continue
            else
                echo "Abort!"
                break
            fi
        else
            # success
            break
        fi
    done

    verbose_log_end_msg 0
}

hwrev=0

echo `date` $1 >> /tmp/m5pro.log

case "$1" in
start)
    log_action_msg "M5Pro Initializing devices"

    es9820 11 0x24 0x20
    es9820 11 0x25 0x21

    es9033  6 0x4C 0x48
    es9033  7 0x4C 0x48
    es9033  8 0x4C 0x48
    es9033  9 0x4C 0x48
    es9033 10 0x4C 0x48

    src4392_out  6 0x70 0 1
    src4392_out  7 0x70 0 1
    src4392_out  8 0x70 0 1
    src4392_out  9 0x70 0 1
    src4392_out 10 0x70 0 1

    src4392_in 12 0x70
    src4392_in 13 0x70

    # setup gpio inputs
    # does not do anything because input is already the default
    gpio_setup_in factory_n
    gpio_setup_in hwid0
    gpio_setup_in hwid1
    gpio_setup_in hwid2
    gpio_setup_in hwid3
    gpio_setup_in hwrev0
    gpio_setup_in hwrev1
    gpio_setup_in swoff
    gpio_setup_in trigin1_n
    gpio_setup_in trigin2_n
    gpio_setup_in trigin3_n
    gpio_setup_in trigin4_n

    # setup gpio outputs
    gpio_setup_out trigout1  0
    gpio_setup_out trigout2  0
    gpio_setup_out trigout3  0
    gpio_setup_out trigout4  0
    gpio_setup_out trigout5  0
    gpio_setup_out pwrled    1  # default power led to on
    gpio_setup_out bootcompl 0
    gpio_setup_out pwroff    0
    gpio_setup_out clkselo1  0
    gpio_setup_out clkselo2  0
    gpio_setup_out clkselo3  0
    gpio_setup_out clkselo4  0
    gpio_setup_out clkselo5  0

    nvme_init

    pulseaudio_init

    # signal boot finished to PMIC
    gpioset `gpiofind bootcompl`=1  # signal boot complete, TODO: should be in app

    verbose_log_success_msg "M5Pro Initialization done"
    ;;

restart|reload|force-reload)
    /etc/init.d/m5pro start
    ;;

shutdown)
    echo "################## m5pro shutdown #########################"
    gpioset `gpiofind pwroff`=1 # signal shutdown instead of reboot
    ;;

reboot)
    echo "################## m5pro reboot ###########################"
    ;;
esac

exit 0
