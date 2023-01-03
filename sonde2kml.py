#!/usr/bin/env python
#

import argparse
import csv
import logging
import os
import re

from datetime import datetime
from pathlib import Path
from string import Template

from simplekml import Kml
from simplekml import GxAltitudeMode
from simplekml import ListItemType
from simplekml import AltitudeMode

__version__ = "0.0.1"

TMPDIR = '/tmp'
POINTS_SPACING = 25

DESCRIPTION = Template("""Frame: $frame
Serial: $serial
Altitude: $alt m
Velocity: Verticale: $vel_v m/s
Velocity: Horizontale: $vel_h m/s
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
      points.append(row)
  logging.info('Read file "%s", number of points: %d', logfile, len(points))
  return points

def export_kml(logfile, spacing=POINTS_SPACING, target_dir=TMPDIR):
  points = read_log(logfile)
  kml = Kml(name="Weather Balloon", open=1)
  doc = kml.newdocument()
  doc.liststyle.listitemtype = ListItemType.check
  doc.name = "Weather balloon"
  doc.visibility = 1
  doc.open = 1
  doc.atomauthor = "0x9900"
  doc.atomlink = "https://0x9900.com/category/hamradio.html"
  doc.description = (f"Weather balloon {logfile.type} / {logfile.number} \n"
                     f"Departed on {logfile.datetime} UTC\n"
                     f"{len(points)} metrics captured")

  folder = doc.newfolder(name=f"{logfile.number} Points", open=0)
  line = []
  for idx, row in enumerate(points):
    if idx < len(points) - 10 and idx % spacing != 0:
      continue
    coords = (row['lon'], row['lat'], row['alt'])
    line.append(coords)
    kml_pnt = folder.newpoint(name=idx, coords=[coords],
                              gxaltitudemode=GxAltitudeMode.relativetoseafloor)
    kml_pnt.description = DESCRIPTION(row)
    kml_pnt.style.iconstyle.icon.href = 'https://bsdworld.org/balloon.png'
    kml_pnt.style.labelstyle.scale = 0.75
    kml_pnt.style.iconstyle.color = 'ffffff00'
    kml_pnt.style.iconstyle.scale = 1.25

  folder = doc.newfolder(name=f"{logfile.number} Altitude line", open=0)
  kml_line = folder.newlinestring(name='Altitude', coords=line)
  kml_line.extrude = 1
  kml_line.altitudemode = AltitudeMode.relativetoground

  kml_file = os.path.join(target_dir, f"{logfile.basename}.kml")
  logging.info('Generating .kml file: "%s"', kml_file)
  kml.savekmz(kml_file)

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
  logging.info('Reading "%s" directory', directory)
  logfiles = []
  for filename in os.listdir(directory):
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
  cmds.add_argument('-d', '--dir', default='/tmp', help='Directory containing the log files')
  cmds.add_argument('-f', '--file', help="Full path of the file to process")
  parser.add_argument('-s', '--spacing', type=int, default=POINTS_SPACING,
                      help='Spacing between points [default: %(default)d]')
  parser.add_argument('-t', '--target-dir', default=TMPDIR,
                      help='Directory for ".kml" files [default: %(default)s]')
  opts = parser.parse_args()

  if opts.file:
    logfile = LogName(opts.file)
  else:
    logfiles = select_file(opts.dir)
    logfile = logfiles[-1]
  export_kml(logfile, spacing=opts.spacing, target_dir=opts.target_dir)

if __name__ == "__main__":
  main()
