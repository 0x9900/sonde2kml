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

FILES=$(grep '^20.*_sonde.log' $TMPFILE)
COUNT=$(awk -F : '/Number of regular files transferred/{print $2}' $TMPFILE)

if [[ $((COUNT)) > 0 ]]; then
    echo "----------------------------------------------------------------------"
    for file in $FILES; do
	sonde2kml -f ${DSTDIR}/${file} --zip
    done
fi
