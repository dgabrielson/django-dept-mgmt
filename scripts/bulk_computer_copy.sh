#!/bin/bash

# New Computers Script:
# Prepare data file with contents: SERIAL WIFI ETHER BLUE on each line.
# Ensure the file ends with a newline; otherwise read misses the last entry.

if [[ "$1" == "" ]]; then
    echo "You must supply a computer PK to copy"
    echo "./bulk_computer_copy.sh PK NEWNAME BULKFILE"
    exit
fi

if [[ "$2" == "" ]]; then
    echo "You must supply a new computer name for the copies"
    echo "./bulk_computer_copy.sh PK NEWNAME BULKFILE"
    exit
fi

if [[ "$3" == "" ]]; then
    echo "You must supply a source file for the bulk details"
    echo "./bulk_computer_copy.sh PK NEWNAME BULKFILE"
    exit
fi

cat "$3" | while read serial wifi ether blue ;
do
    CMD="./manage.py it_mgmt computer_copy \"$1\" -c \"$2\" -s $serial -i \"en0,e,$ether;en1,w,$wifi;bluetooth,b,$blue\""
    echo ${CMD}
    eval ${CMD}
done
