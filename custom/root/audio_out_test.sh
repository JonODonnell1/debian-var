#!/bin/bash
SOURCE1="SigGen -r 192000 -d 60 -n 60 -f 100 -F 200"
SOURCE2="SigGen -r 192000 -d 60 -n 60 -f 300 -F 400"
SOURCE3="SigGen -r 192000 -d 60 -n 60 -f 500 -F 600"
SOURCE4="SigGen -r 192000 -d 60 -n 60 -f 700 -F 800"
SOURCE5="SigGen -r 192000 -d 60 -n 60 -f 900 -F 1000"
interleave -n8 <( $SOURCE1 ) <( $SOURCE2 ) <( $SOURCE3 ) <( $SOURCE4 ) <( $SOURCE5 ) | aplay --device=plughw:CARD=dummyaudio1,DEV=0 --file-type=RAW --channels=10 --rate=192 --format=S32_LE
