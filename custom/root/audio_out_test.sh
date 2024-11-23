#!/bin/bash
SOURCE1="SigGen -r 192000 -d 60 -n 60 -f 100 -F 200"
SOURCE2="SigGen -r 192000 -d 60 -n 60 -f 125 -F 250"
SOURCE3="SigGen -r 192000 -d 60 -n 60 -f 150 -F 300"
SOURCE4="SigGen -r 192000 -d 60 -n 60 -f 175 -F 350"
SOURCE5="SigGen -r 192000 -d 60 -n 60 -f 225 -F 450"
SOURCE6="SigGen -r 192000 -d 60 -n 60 -f 275 -F 550"
SOURCE7="SigGen -r 192000 -d 60 -n 60 -f 325 -F 650"
SOURCE8="SigGen -r 192000 -d 60 -n 60 -f 375 -F 750"
interleave -n8 <( $SOURCE1 ) <( $SOURCE2 ) <( $SOURCE3 ) <( $SOURCE4 ) <( $SOURCE5 ) <( $SOURCE6 ) <( $SOURCE7 ) <( $SOURCE8 ) | aplay --device=plughw:CARD=dummyaudio1,DEV=0 --file-type=RAW --channels=16 --rate=192 --format=S32_LE
