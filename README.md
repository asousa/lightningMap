## Synopsis

A tool for displaying real-time lightning data (or any lat, long, magnitude dataset) on a nice slippymap.

GLD2.html is the client page; GLD_server_websocket.py is the backend.

## Use

1: Start Python webserver:
  sudo python -m SimpleHTTPServer 80
2: Start GLD_server_websocket.py

3: Load GLD2.html

Root paths to the data directories are set in GLD_server_instance.py:
  -self.GLD_root : the GLD data root directory
  -self.NLDN_root : the NLDN data root directory

Data is sorted into folders, by day:
  [root_dir]/YYYY-MM-DD/GLD-YYYYMMDDhhmmss.dat

## To use with other data sources:

You'll need to set the root path to each source, and configure GLD_file_tools to read your new data.

Each line of a data file has the following structure:

0 | Year | Month | Day | Hour | Minute | second | Nanoseconds | Lat | Long | Intensity + ~(12 don't care entries)