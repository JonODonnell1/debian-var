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
    verbose_log_begin_msg "$MODEL pulseaudio_init"

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
    verbose_log_begin_msg "$MODEL nvme_init"
    if [ `df | grep /dev/nvme0n1 | wc -l` -eq 0 ]; then
        if [ ! -c /dev/nvme0 ]; then
            log_action_msg "ERROR: $MODEL NVMe Drive found!"
            exit 1
        fi
        if [ ! -b /dev/nvme0n1 ]; then
            log_action_msg "ERROR: $MODEL NVMe Drive Partitions found!"
            exit 1
        fi
        if [ `blkid | grep nvme | wc -l` -eq 0 ]; then
            verbose_log_action_msg "$MODEL Creating NVMe FS"
            mkfs.ext4 /dev/nvme0n1
        fi
        if [ ! -d /mnt/data ]; then
            verbose_log_action_msg "$MODEL Creating NVMe mount point"
            mkdir -p /mnt/data
            chmod 777 /mnt/data
        fi
        UUID=`blkid -o value /dev/nvme0n1 | head -n1`
        if [ `grep ${UUID} /etc/fstab | wc -l` -eq 0 ]; then
            verbose_log_action_msg "$MODEL Adding NVMe to /etc/fstab"
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
    verbose_log_begin_msg "$MODEL gpio_setup_out $name $value"
    gpio=`gpiofind $name`
    if [ -z "$gpio" ]; then
        log_action_msg "ERROR: $MODEL Unable to find GPIO '$name'"
        exit 1
    fi
    gpioset $gpio=$value
    verbose_log_end_msg 0
}

gpio_setup_in(){
    name=$1
    verbose_log_begin_msg "$MODEL gpio_setup_in $name $value"
    gpio=`gpiofind $name`
    if [ -z "$gpio" ]; then
        log_action_msg "ERROR: $MODEL Unable to find GPIO '$name'"
        exit 1
    fi
    value=`gpioget $gpio`
    verbose_log_end_msg 0
}

es9820(){
    i2c_bus=$1
    i2c_sync_addr=$2
    i2c_addr=$3

    verbose_log_begin_msg "$MODEL Initializing es9820 on i2c-${i2c_bus} @ ${i2c_sync_addr}/${i2c_addr}..."

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

    verbose_log_begin_msg "$MODEL Initializing es9033 on i2c-${i2c_bus} @ ${i2c_sync_addr}/${i2c_addr}..."

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
    i2c_bus=$1 # 6|7|8|9|10
    i2c_addr=$2
    freq=$3 # 48000, 96000, 192000, 44100, 88200, 176400
    bitperfect=$4 # 0,1 (bitperfect uses port B and can only be used for i2c_addr==6)
    #  if !bitperfect & freq==44100|88200|176400, SAI2 must be playing dummy 44.1k stream to generate clock
    #  if bitperfect, freq must match rate on SAI2

    verbose_log_begin_msg "$MODEL Initializing src4392 for output on i2c-${i2c_bus} @ ${i2c_addr}..."

    if [ $bitperfect -eq 0 ]; then
        if [ $freq -eq 48000 ]; then
            reg_p0_06=0x00  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            reg_p0_07=0x7C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=SRC (0x18), TXDIV 512 (0x60), TXCLK=MCLK (0x00)
            reg_p2_06=0x40  #  Ch1 48kHz, Level 2 accuracy
            reg_p2_07=0x40  #  Ch2 48kHz, Level 2 accuracy
        elif [ $freq -eq 96000 ]; then
            reg_p0_06=0x00  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            reg_p0_07=0x3C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=SRC (0x18), TXDIV 256 (0x20), TXCLK=MCLK (0x00)
            reg_p2_06=0x50  #  Ch1 96kHz, Level 2 accuracy
            reg_p2_07=0x50  #  Ch2 96kHz, Level 2 accuracy
        elif [ $freq -eq 192000 ]; then
            reg_p0_06=0x00  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            reg_p0_07=0x1C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=SRC (0x18), TXDIV 128 (0x00), TXCLK=MCLK (0x00)
            reg_p2_06=0x70  #  Ch1 192kHz, Level 2 accuracy
            reg_p2_07=0x70  #  Ch2 192kHz, Level 2 accuracy
        elif [ $freq -eq 44100 ]; then
            reg_p0_06=0x00  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            reg_p0_07=0x7C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=SRC (0x18), TXDIV 512 (0x60), TXCLK=MCLK (0x00)
            reg_p2_06=0x00  #  Ch1 44.1kHz, Level 2 accuracy
            reg_p2_07=0x00  #  Ch2 44.1kHz, Level 2 accuracy
        elif [ $freq -eq 88200 ]; then
            reg_p0_06=0x00  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            reg_p0_07=0x3C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=SRC (0x18), TXDIV 256 (0x20), TXCLK=MCLK (0x00)
            reg_p2_06=0x10  #  Ch1 88.2kHz, Level 2 accuracy
            reg_p2_07=0x10  #  Ch2 88.2kHz, Level 2 accuracy
        elif [ $freq -eq 176400 ]; then
            reg_p0_06=0x00  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            reg_p0_07=0x1C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=SRC (0x18), TXDIV 128 (0x00), TXCLK=MCLK (0x00)
            reg_p2_06=0x30  #  Ch1 176.4kHz, Level 2 accuracy
            reg_p2_07=0x30  #  Ch2 176.4kHz, Level 2 accuracy
        fi
    else
        if [ $freq -eq 48000 ]; then
            reg_p0_06=0x03  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 512x LRCK (0x03)
            reg_p0_07=0x6C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=Port B (0x08), TXDIV 512 (0x60), TXCLK=MCLK (0x00)
            reg_p2_06=0x40  #  Ch1 48kHz, Level 2 accuracy
            reg_p2_07=0x40  #  Ch2 48kHz, Level 2 accuracy
        elif [ $freq -eq 96000 ]; then
            reg_p0_06=0x01  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 256x LRCK (0x01)
            reg_p0_07=0x2C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=Port B (0x08), TXDIV 256 (0x20), TXCLK=MCLK (0x00)
            reg_p2_06=0x50  #  Ch1 96kHz, Level 2 accuracy
            reg_p2_07=0x50  #  Ch2 96kHz, Level 2 accuracy
        elif [ $freq -eq 192000 ]; then
            reg_p0_06=0x00  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            reg_p0_07=0x0C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=Port B (0x08), TXDIV 128 (0x00), TXCLK=MCLK (0x00)
            reg_p2_06=0x70  #  Ch1 192kHz, Level 2 accuracy
            reg_p2_07=0x70  #  Ch2 192kHz, Level 2 accuracy
        elif [ $freq -eq 44100 ]; then
            reg_p0_06=0x03  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 512x LRCK (0x03)
            reg_p0_07=0x6C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=Port B (0x08), TXDIV 512 (0x60), TXCLK=MCLK (0x00)
            reg_p2_06=0x00  #  Ch1 44.1kHz, Level 2 accuracy
            reg_p2_07=0x00  #  Ch2 44.1kHz, Level 2 accuracy
        elif [ $freq -eq 88200 ]; then
            reg_p0_06=0x01  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 256x LRCK (0x01)
            reg_p0_07=0x2C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=Port B (0x08), TXDIV 256 (0x20), TXCLK=MCLK (0x00)
            reg_p2_06=0x10  #  Ch1 88.2kHz, Level 2 accuracy
            reg_p2_07=0x10  #  Ch2 88.2kHz, Level 2 accuracy
        elif [ $freq -eq 176400 ]; then
            reg_p0_06=0x00  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            reg_p0_07=0x0C  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=Port B (0x08), TXDIV 128 (0x00), TXCLK=MCLK (0x00)
            reg_p2_06=0x30  #  Ch1 176.4kHz, Level 2 accuracy
            reg_p2_07=0x30  #  Ch2 176.4kHz, Level 2 accuracy
        fi
    fi
    if [ $i2c_bus -eq 6 ]; then
        reg_p2_04=0x88      # Source 1, Left
        reg_p2_05=0x84      # Source 1, Right
    elif [ $i2c_bus -eq 7 ]; then
        reg_p2_04=0x48      # Source 2, Left
        reg_p2_05=0x44      # Source 2, Right
    elif [ $i2c_bus -eq 8 ]; then
        reg_p2_04=0xC8      # Source 3, Left
        reg_p2_05=0xC4      # Source 3, Right
    elif [ $i2c_bus -eq 9 ]; then
        reg_p2_04=0x28      # Source 4, Left
        reg_p2_05=0x24      # Source 4, Right
    elif [ $i2c_bus -eq 10 ]; then
        reg_p2_04=0xA8      # Source 5, Left
        reg_p2_05=0xA4      # Source 5, Right
    fi

    i=0
    while [ true ]; do
        i=$(($i+1))

        # TODO: Simple DIT.  No SRC/clock divider for now
        i2cprog $i2c_bus $i2c_addr <<____________EOF_i2cprog
            0x7F 0x00  # Register Page 0
            0x01 0x80  #  Reset
            0x03 0x41  #  I2S Port A: 24 Bit Audio I2S (0x01), Clock Slave (0x00), AOUTS=loopback (0x00), Mute (0x40)
            0x04 0x00  #  I2S Port A: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            0x05 0x41  #  I2S Port B: 24 Bit Audio I2S (0x01), Clock Slave (0x00), BOUTS=loopback (0x00), Mute (0x40)
            0x06 $reg_p0_06
            0x07 $reg_p0_07
            0x08 0x08  #  DIT: TX+ Enable (0x00), TX+ Unmute (0x00), AESOUT Enable (0x00), TXBT Enable (0x08), LDMUX=AES3 (0x00), AESMUX=AES3 (0x00), BYPMUX=RX1 (0x00)
            0x09 0x01  #  DIT: TXCUS=SPI/I2C (0x01), VALSEL=reg (0x00)
            0x0D 0x08  #  DIR: RXMUX=RX1 (0x00), RXCLK=MCLK (0x08), RXBT=Diabled (0x00)
            0x0E 0x00  #  DIR: RXCLOE=Disabled (0x00), RXCKOD=Passthrough (0x00), RXAMLL=disabled (0x00), LOL=PLl2 Stop (0x00)
            0x0F 0x22  #  DIR PLL1: 24.576MHz / 2 (P) * 8.0000 (J.D) = 98.304MHz (P=2, J=8, D=0) -- DOES NOT MATTER FOR OUTPUTS
            0x10 0x00  #
            0x11 0x00  #
            0x1B 0x00  #  GPIO1: Low (0x00)
            0x1C 0x00  #  GPIO2: Low (0x00)
            0x1D 0x00  #  GPIO3: Low (0x00)
            0x1E 0x00  #  GPIO4: Low (0x00)
            0x2D 0x00  #  SRC: SRCIS=Port A (0x00), SRCCLK=MCLK (0x00), MUTE=Disabled (0x00), TRACK=independent (0x00)
            0x2E 0x00  #  SRC: IGRP=64 (0x00), DDN=Decimation (0x00), DEM=No De-emphasis (0x00), AUTODEM=Disabled (0x00)
            0x2F 0x00  #  SRC: OWL=24 (0x00)
            0x30 0x00  #  SRC: Left Atten=0dB (0x00)
            0x31 0x00  #  SRC: Right Atten=0dB (0x00)
            0x08 0x00  #  DIT: TX+ Enable (0x00), TX+ Unmute (0x00), AESOUT Enable (0x00), TXBT Disable (0x00), LDMUX=AES3 (0x00), AESMUX=AES3 (0x00), BYPMUX=RX1 (0x00)
            0x01 0x3F  #  All on
            0x7F 0x02  # Register Page 2
            0x00 0x20  #  Ch1 S/PDIF, Digital Audio, Copy Permitted, No Pre-emphasis
            0x01 0x20  #  Ch2 S/PDIF, Digital Audio, Copy Premitted, No Pre-emphasis
            0x02 0x00  #  Ch1 General Category, Original (Audio Precision does not understand 1st-gen flag)
            0x03 0x00  #  Ch2 General Category, Original (Audio Precision does not understand 1st-get flag)
            0x04 $reg_p2_04
            0x05 $reg_p2_05
            0x06 $reg_p2_06
            0x07 $reg_p2_07
            0x7F 0x00  # Register Page 0
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

    if [ $i2c_bus -eq 6 ]; then
        if [ $freq -eq 192000 -o $freq -eq 96000 -o $freq -eq 48000 ]; then
            gpioset `gpiofind clkselo1`=0
        else
            gpioset `gpiofind clkselo1`=1
        fi
    elif [ $i2c_bus -eq 7 ]; then
        if [ $freq -eq 192000 -o $freq -eq 96000 -o $freq -eq 48000 ]; then
            gpioset `gpiofind clkselo2`=0
        else
            gpioset `gpiofind clkselo2`=1
        fi
    elif [ $i2c_bus -eq 8 ]; then
        if [ $freq -eq 192000 -o $freq -eq 96000 -o $freq -eq 48000 ]; then
            gpioset `gpiofind clkselo3`=0
        else
            gpioset `gpiofind clkselo3`=1
        fi
    elif [ $i2c_bus -eq 9 ]; then
        if [ $freq -eq 192000 -o $freq -eq 96000 -o $freq -eq 48000 ]; then
            gpioset `gpiofind clkselo4`=0
        else
            gpioset `gpiofind clkselo4`=1
        fi
    elif [ $i2c_bus -eq 10 ]; then
        if [ $freq -eq 192000 -o $freq -eq 96000 -o $freq -eq 48000 ]; then
            gpioset `gpiofind clkselo5`=0
        else
            gpioset `gpiofind clkselo5`=1
        fi
    fi
    verbose_log_end_msg 0
}

src4392_in(){
    i2c_bus=$1
    i2c_addr=$2

    verbose_log_begin_msg "$MODEL Initializing src4392 for input on i2c-${i2c_bus} @ ${i2c_addr}..."

    i=0
    while [ true ]; do
        i=$(($i+1))

        i2cprog $i2c_bus $i2c_addr <<____________EOF_i2cprog
            0x7F 0x00  # Register Page 0
            0x01 0x80  #  Reset
            0x03 0x31  #  I2S Port A: 24 Bit Audio I2S (0x01), Clock Slave (0x00), AOUT=SRC (0x30), Un-Mute (0x00)
            0x04 0x00  #  I2S Port A: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            0x05 0x41  #  I2S Port B: 24 Bit Audio I2S (0x01), Clock Slave (0x00), BOUTS=loopback (0x00), Mute (0x40)
            0x06 0x00  #  I2S Port B: MCLK Source MCLK (0x00), MCLK Freq = 128x LRCK (0x00)
            0x07 0x04  #  DIT: Data slip (0x00), VALID (0x00), BLSM Output (0x04), TXIS=Port A (0x00), TXDIV 128 (0x00), TXCLK=MCLK (0x00)
            0x08 0x07  #  DIT: TX+ Disabled (0x01), TX+ Mute (0x02), AESOUT Disable (0x04), TXBT Disable (0x00), LDMUX=AES3 (0x00), AESMUX=AES3 (0x00), BYPMUX=RX1 (0x00)
            0x09 0x00  #  DIT: TXCUS=static (0x00), VALSEL=reg (0x00)
            0x0D 0x08  #  DIR: RXMUX=RX1 (0x00), RXCLK=MCLK (0x08), RXBT=Enabled??? (0x00)
            0x0E 0x08  #  DIR: RXCLOE=Disabled (0x00), RXCKOD=Passthrough (0x00), RXAMLL=enabled (0x08), LOL=PLl2 Stop (0x00)
            0x0F 0x22  #  DIR PLL1: 24.576MHz / 2 (P) * 8.0000 (J.D) = 98.304MHz (P=2, J=8, D=0)
            0x10 0x00  #
            0x11 0x00  #
            0x1B 0x00  #  GPIO1: Low (0x00)
            0x1C 0x00  #  GPIO2: Low (0x00)
            0x1D 0x00  #  GPIO3: Low (0x00)
            0x1E 0x00  #  GPIO4: Low (0x00)
            0x2D 0x02  #  SRC: SRCIS=DIR (0x02), SRCCLK=MCLK (0x00), MUTE=Disabled (0x00), TRACK=independent (0x00)
            0x2E 0x20  #  SRC: IGRP=64 (0x00), DDN=Decimation (0x00), DEM=No De-emphasis (0x00), AUTODEM=Enabled (0x20)
            0x2F 0x00  #  SRC: OWL=24 (0x00)
            0x30 0x00  #  SRC: Left Atten=0dB (0x00)
            0x31 0x00  #  SRC: Right Atten=0dB (0x00)
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

gpio_init(){
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
}

gpio_read(){
    gpio=$1
    gpioget `gpiofind "$gpio"`
}

echo `date` $1 >> /tmp/$MODEL.log

case "$1" in
start)
    export MODEL="M5Pro/M3"
    log_action_msg "$MODEL Initializing devices"

    gpio_init

    hwid0=$(gpio_read hwid0)
    hwid1=$(gpio_read hwid1)
    hwid2=$(gpio_read hwid2)
    hwid3=$(gpio_read hwid3)
    hwid=$(( $hwid0 + 2*hwid1 + 4*hwid2 + 8*hwid3 ))
    HWID_M5PRO=0
    HWID_M3=1
    if [ $hwid -eq $HWID_M5PRO ]; then
        export MODEL=M5Pro
    else
        export MODEL=M3
    fi

    hwrev0=$(gpio_read hwrev0)
    hwrev1=$(gpio_read hwrev1)
    hwrev=$(( $hwrev0 + 2*hwrev1 ))

    if [ $hwid -eq $HWID_M5PRO ]; then
        es9820 11 0x24 0x20
    fi
    es9820 11 0x25 0x21

    es9033  6 0x4C 0x48
    es9033  7 0x4C 0x48
    es9033  8 0x4C 0x48
    if [ $hwid -eq $HWID_M5PRO ]; then
        es9033  9 0x4C 0x48
        es9033 10 0x4C 0x48
    fi

    src4392_out  6 0x70 192000 0
    src4392_out  7 0x70 192000 0
    src4392_out  8 0x70 192000 0
    if [ $hwid -eq $HWID_M5PRO ]; then
        src4392_out  9 0x70 192000 0
        src4392_out 10 0x70 192000 0
    fi

    src4392_in 12 0x70
    if [ $hwid -eq $HWID_M5PRO ]; then
        src4392_in 13 0x70
    fi

    if [ $hwid -eq $HWID_M5PRO ]; then
        nvme_init
    fi

    pulseaudio_init

    # signal boot finished to PMIC
    gpioset `gpiofind bootcompl`=1  # signal boot complete, TODO: should be in app

    verbose_log_success_msg "$MODEL Initialization done"
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
