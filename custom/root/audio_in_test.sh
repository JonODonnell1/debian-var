#!/bin/bash
REC_DUR_S=1
DISCARD_S=2
FILENAME="in"

SRATE=192000
CHANNELS=16

BYTES_PER_SAMPLE=4

DUR=$(( $REC_DUR_S+$DISCARD_S ))
START_BYTE=$(( $DISCARD_S*$CHANNELS*$SRATE*$BYTES_PER_SAMPLE+1 ))

arecord --device=hw:CARD=dummyaudio1,DEV=0 --file-type=RAW --channels=$CHANNELS --rate=$SRATE --format=S32_LE --duration=$DUR --disable-resample --disable-channels --disable-format --disable-softvol --dump-hw-params | tail --bytes=+$START_BYTE | deinterleave -n8 $FILENAME.1 $FILENAME.2 $FILENAME.3 $FILENAME.4 $FILENAME.5 $FILENAME.6 $FILENAME.7 $FILENAME.8
