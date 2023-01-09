#!/bin/bash
# Download the radiosonde log files into my laptop, then generate the
# kml file if a new file has been downloaded

SRCDIR="/tmp/log"
DSTDIR="/Volumes/WDPassport/tmp/sondes"
TMPFILE=$(mktemp -t "getsonde")

cleanup() {
    rm -f $TMPFILE
    exit 0
}

trap "cleanup" EXIT INT TERM

rsync -e ssh --stats -avH "sonderx.home:${SRCDIR}/" ${DSTDIR} | \
    tee $TMPFILE

COUNT=$(awk -F : '/Number of regular files transferred/{print $2}' $TMPFILE)

if [[ $((COUNT)) > 0 ]]; then
    sonde2kml -d ${DSTDIR} --zip
fi
