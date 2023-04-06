
# Sonde2KML

Read the radiosonde log file and generate a `.kml` file for [Google Earth][1].

Works with logs coming from [radiosonde_auto_rx][2]

You can find more information on how to track weather balloons at [https://0x9900.com/][3]

## Usage
```
usage: sonde2kml.py [-h] (-d DIR | -f FILE) [-s SPACING] [-t TARGET_DIR] [-z]

Purge old dxcc images

options:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     Directory containing the log files
  -f FILE, --file FILE  Full path of the file to process
  -s SPACING, --spacing SPACING
                        Spacing between points [default: 100]
  -t TARGET_DIR, --target-dir TARGET_DIR
                        Directory for ".kml" files [default: /tmp]
  -z, --zip             Compress the output file [default: False]
```

## Example

In the following example `sonde2kml` uses the last log file to generate the `.kml` file.

```
√ fred@sonderx$ sonde2kml --spacing 150 --file /tmp/sondes/20230117-112338_U2450614_RS41_404001_sonde.log
09:07:34 INFO: zip: False, spacing 150, target_dir: /tmp
09:07:34 INFO: Read file "/tmp/sondes/20230117-112338_U2450614_RS41_404001_sonde.log", number of points: 4473
09:07:34 INFO: Saving file /tmp/20230117-112338_U2450614_RS41_404001_sonde.kml
```

## Output

![Weahter Sonde path on Google Earth](misc/GoogleEarth-Sonde.png)

## Examples

  - [20230116-230717_U2450615_RS41_404000_sonde.kmz][4]
  - [20230117-112338_U2450614_RS41_404001_sonde.kmz][5]
  - [20230117-230557_U2450622_RS41_404001_sonde.kmz][6]
  - [20230118-110354_U2540033_RS41_404001_sonde.kmz][7]
  - [20230118-230610_U2540023_RS41_404001_sonde.kmz][8]
  - [20230119-110735_U2450623_RS41_404001_sonde.kmz][9]



[1]: https://www.google.com/earth/versions/#earth-pro
[2]: https://github.com/projecthorus/radiosonde_auto_rx
[3]: https://0x9900.com/tracking-weather-balloons/

[4]: misc/20230116-230717_U2450615_RS41_404000_sonde.kmz
[5]: misc/20230117-112338_U2450614_RS41_404001_sonde.kmz
[6]: misc/20230117-230557_U2450622_RS41_404001_sonde.kmz
[7]: misc/20230118-110354_U2540033_RS41_404001_sonde.kmz
[8]: misc/20230118-230610_U2540023_RS41_404001_sonde.kmz
[9]: misc/20230119-110735_U2450623_RS41_404001_sonde.kmz
