#!/bin/bash

# DATA_DIR=$(cat sensors.py | grep "DATA_DIR =" | cut -d"'" -f2)
DATA_DIR=$1

cd $DATA_DIR

for j in $(ls *.h264)
do
	filename=${j%.*}
	filename=$filename.mp4
	MP4Box -add $j $filename &> /dev/null # Essential to run quickly when called from python script
	rm $j
done
