#!/bin/bash

# cd $(cat sensors.py | grep "DATA_DIR =" | cut -d"'" -f2)

if [ -n "$1" ]; then
	cd $1
fi

for j in $(ls *.h264 2>/dev/null)
do
	filename=${j%.*}
	filename=$filename.mp4
	MP4Box -add $j $filename &> /dev/null # Essential to run quickly when called from python script
	rm $j
done
