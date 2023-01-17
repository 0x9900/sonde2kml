#!/bin/bash
# Download the radiosonde log files into my laptop, then generate the
# kml file if a new file has been downloaded

TMPFILE=$(mktemp -t "getsonde")
SRCDIR="/tmp/log"
# DSTDIR="/Volumes/WDPassport/tmp/sondes"
DSTDIR="/tmp/sondes"
SPACING=${1:-50}

cleanup() {
    rm -f $TMPFILE
    exit 0
}

trap "cleanup" EXIT INT TERM

rsync -e ssh --stats -avH "sonderx.home:${SRCDIR}/" ${DSTDIR} > ${TMPFILE}

FILES=($(egrep '^\d+-\d+_.*_sonde.log' $TMPFILE))
COUNT=$(awk -F : '/Number of regular files transferred/{print $2}' $TMPFILE)

if [[ $((COUNT)) > 0 ]]; then
    for file in "${FILES[@]}"; do
	./sonde2kml.py -s ${SPACING} -f ${DSTDIR}/"${file}" --zip
    done
else
    echo "No new file to process"
fi
