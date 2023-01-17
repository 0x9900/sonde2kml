#!/usr/bin/env python
#

import argparse
import csv
import logging
import math
import os
import re
import sys

from datetime import datetime
from pathlib import Path
from string import Template
from dateutil import tz

from simplekml import Kml
from simplekml import GxAltitudeMode
from simplekml import ListItemType
from simplekml import AltitudeMode

__version__ = "0.0.4"

TMPDIR = '/tmp'
POINTS_SPACING = 100

DESCRIPTION = Template("""Serial: $serial
Frame: $frame
UTC Time: $utc_date
Local Time: $localtime

Altitude: $alt m
Max Altitude: $max_alt
Velocity: Vertical: $vel_v m/s
Velocity: Horizontal: $vel_h m/s
Speed: $speed m/s
Heading: $headingº
Temperature: $tempºC

Battery: $batt_v Volt
Frequency: $freq_mhz MHz
SNR: $snr""").safe_substitute


def read_log(logfile):
  points = []
  with open(logfile.fullname, encoding="ASCII", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      for key, val in row.items():
        try:
          row[key] = float(val)
        except ValueError:
          pass
      points.append(row)
  logging.info('Read file "%s", number of points: %d', logfile, len(points))
  return points

def export_kml(logfile, spacing=POINTS_SPACING, target_dir=TMPDIR, kzip=False):
  points = read_log(logfile)

  kml = Kml(name=f"Launch: {logfile.datetime.date()} {logfile.datetime.time()}", open=1)
  doc = kml.newdocument()
  doc.liststyle.listitemtype = ListItemType.check
  doc.name = f"Sonde: {logfile.number}"
  doc.visibility = 1
  doc.open = 1
  doc.atomauthor = "0x9900"
  doc.description = (f"Departed on {logfile.datetime} UTC\n"
                     f"Radiosonde type: {logfile.type}\n")

  folder = doc.newfolder(name="Points", open=0)
  max_alt = max(float(d['alt']) for d in points)
  line = []
  for idx, row in enumerate(points):
    coords = (row['lon'], row['lat'], row['alt'])
    line.append(coords)

    if row['alt'] < max_alt and idx < len(points) - 10 and idx % spacing != 0:
      continue

    row['max_alt'] = max_alt
    kml_pnt = folder.newpoint(name=f"Packet: #{idx}", coords=[coords],
                              gxaltitudemode=GxAltitudeMode.relativetoseafloor)
    speed = math.sqrt(float(row['vel_h'])**2 + float(row['vel_v'])**2)
    utc_date = datetime.strptime(row['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
    row['utc_date'] = utc_date.strftime('%x %X')
    utc_date = utc_date.replace(tzinfo=tz.tzutc())
    row['localtime'] = utc_date.astimezone(tz.tzlocal()).strftime('%x %X')
    row['speed'] = f"{speed:.2f}"
    kml_pnt.description = DESCRIPTION(row)
    if row['alt'] < max_alt:
      kml_pnt.style.iconstyle.icon.href = 'https://bsdworld.org/balloon.png'
    else:
      kml_pnt.style.iconstyle.icon.href = 'https://bsdworld.org/marker.png'

    kml_pnt.style.labelstyle.scale = 0.75
    kml_pnt.style.iconstyle.color = 'ffffff00'
    kml_pnt.style.iconstyle.scale = 1.25

  folder = doc.newfolder(name="Altitude line", open=0)
  kml_line = folder.newlinestring(name='Altitude', coords=line)
  kml_line.extrude = 1
  kml_line.altitudemode = AltitudeMode.relativetoground

  if kzip:
    out_file = os.path.join(target_dir, f"{logfile.basename}.kmz")
    kml.savekmz(out_file)
  else:
    out_file = os.path.join(target_dir, f"{logfile.basename}.kml")
    kml.save(out_file)
  logging.info('Saving file %s', out_file)

class LogName:
  __slots__ = ['fullname', 'basename', 'fields']
  RE_ = re.compile(
    r'^(?P<date>\d+)-(?P<time>\d+)_(?P<number>\w+)_(?P<type>[\w-]+)_(?P<freq>\d+)_.*$'
  )
  def __init__(self, filename):
    self.fullname = filename
    self.basename = Path(filename).stem
    match = LogName.RE_.match(self.basename)
    if not match:
      raise OSError('Filename format error')
    fields = match.groupdict()
    packet_date = datetime.strptime(f'{fields["date"]}-{fields["time"]}', '%Y%m%d-%H%M%S')
    self.fields = fields
    self.fields['datetime'] = packet_date

  def __lt__(self, other):
    return ((self.datetime.timestamp()) < (other.datetime.timestamp()))

  def __gt__(self, other):
    return ((self.datetime.timestamp()) > (other.datetime.timestamp()))

  def __le__(self, other):
    return ((self.datetime.timestamp()) <= (other.datetime.timestamp()))

  def __ge__(self, other):
    return ((self.datetime.timestamp()) >= (other.datetime.timestamp()))

  def __eq__(self, other):
    return (self.datetime.timestamp() == other.datetime.timestamp())

  def __str__(self):
    return self.fullname

  def __repr__(self):
    return f'<LogName> {str(self)}'

  @property
  def datetime(self):
    return self.fields['datetime']

  @property
  def number(self):
    return self.fields['number']

  @property
  def type(self):
    return self.fields['type']

  @property
  def freq(self):
    return self.fields['freq']


def select_file(directory):
  logfiles = []
  logging.info('Scanning directory "%s"', directory)
  for filename in os.listdir(directory):
    if not filename.endswith('.log'):
      continue
    try:
      log_file = LogName(os.path.join(directory, filename))
    except OSError:
      logging.debug(filename)
      continue
    logfiles.append(log_file)

  return sorted(logfiles)


def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  parser = argparse.ArgumentParser(description="Purge old dxcc images")
  cmds = parser.add_mutually_exclusive_group(required=True)
  cmds.add_argument('-d', '--dir', help='Directory containing the log files')
  cmds.add_argument('-f', '--file', help="Full path of the file to process")
  parser.add_argument('-s', '--spacing', type=int, default=POINTS_SPACING,
                      help='Spacing between points [default: %(default)d]')
  parser.add_argument('-t', '--target-dir', default=TMPDIR,
                      help='Directory for ".kml" files [default: %(default)s]')
  parser.add_argument('-z', '--zip', action="store_true", default=False,
                      help='Compress the output file [default: %(default)s]')
  opts = parser.parse_args()

  if opts.dir:
    try:
      logfiles = select_file(opts.dir)
    except NotADirectoryError as err:
      logging.error(err)
      sys.exit(os.EX_IOERR)
    if logfiles:
      logfile = logfiles[-1]
    else:
      logging.warning("No radiosonde log file found")
      sys.exit(os.EX_IOERR)
  else:
    if os.path.exists(opts.file):
      logfile = LogName(opts.file)
    else:
      logging.error("File %s Not found", opts.file)
      sys.exit(os.EX_IOERR)

  export_kml(logfile, spacing=opts.spacing, target_dir=opts.target_dir, kzip=opts.zip)

if __name__ == "__main__":
  main()
