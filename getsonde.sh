#!/bin/bash
# Download the radiosonde log files into my laptop, then generate the
# kml file if a new file has been downloaded

SRCDIR="/var/run/radiosonde"
DSTDIR="/Volumes/WDPassport/sondes"
SPACING=${1:-50}

TMPFILE=$(mktemp -t "getsonde")
trap "rm -f ${TMPFILE}; exit 0" EXIT INT TERM

srcdir=${SRCDIR%%/+(/)}/	# clean up trailing slashes
rsync -e ssh --stats -avH "sonderx.home:${srcdir}" ${DSTDIR} > ${TMPFILE}

FILES=($(egrep '^\d+-\d+_.*_sonde.log' $TMPFILE))
COUNT=$(awk -F : '/Number of regular files transferred/{print $2}' $TMPFILE)

if [[ $((COUNT)) > 0 ]]; then
    for file in "${FILES[@]}"; do
	sonde2kml -s ${SPACING} -f ${DSTDIR}/"${file}" --target-dir ${DSTDIR} --zip
    done
else
    echo "No new file to process"
fi
