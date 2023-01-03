
# Sonde 2 KML

Read the radiosonde log file and generate a `.kml` file that can be read with Google Earth.

Works with logs coming from [radiosonde_auto_rx][1]

## Usage
```
usage: sonde2kml.py [-h] (-d DIR | -f FILE) [-s SPACING] [-t TARGET_DIR]

Purge old dxcc images

options:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     Directory containing the log files
  -f FILE, --file FILE  Full path of the file to process
  -s SPACING, --spacing SPACING
                        Spacing between points [default: 25]
  -t TARGET_DIR, --target-dir TARGET_DIR
                        Directory for ".kml" files [default: /tmp]

```

## Example

In the following example `sonde2kml` uses the last log file to generate the `.kml` file.

```
√ fred@sonderx$ sonde2kml --dir auto_rx/log
13:42:24 INFO: Reading "auto_rx/log" directory
13:42:24 INFO: Read file "auto_rx/log/20230103-110742_U2510368_RS41_404000_sonde.log", number of points: 501
13:42:24 INFO: Generating .kml file: "/tmp/20230103-110742_U2510368_RS41_404000_sonde.kml"
```

## Output

![Weahter Sonde path on Google Earth](misc/GoogleEarth-Sonde.png)

[1]: https://github.com/projecthorus/radiosonde_auto_rx
