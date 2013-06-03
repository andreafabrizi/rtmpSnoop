# rtmpSnoop - The RTMP sniffer!

rtmpSnoop lets you to sniff RTMP streams from live TV, online channels and straming services and print the RTMP properties in many formats.  
You can analyse both live and dumped streams.

## Features

* Live sniffing from one ore more interfaces
* Read dumped streams from PCAP files
* Dump the RTMP properties in more formats (simple list, m3u entry or rtmpdump format)
* Easy to use and cross platform!

## Requirements

To run this program you need only **python** (at least 2.7 version) and the **scapy** module.  
To install it on a debian/ubuntu system type `apt-get install python-scapy`.

## Usage

The syntax is quite simple:

```
$python rtmpSnoop.py -h
usage: rtmpSnoop.py [-h] [-i DEVICE | -f PCAPFILE]
                    [--out-list | --out-m3u | --out-rtmpdump] [-p PORT]
                    [--one] [--quiet] [--debug]

rtmpSnoop lets you to grab the RTMP properties from live or dumped streams.

optional arguments:
  -h, --help      show this help message and exit

Input:
  -i DEVICE       Device to sniff on (Default: sniffs on all devices)
  -f PCAPFILE     PCAP file to read from

Output format:
  --out-list      Prints the RTMP data as list (Default)
  --out-m3u       Prints the RTMP data as m3u entry
  --out-rtmpdump  Prints the RTMP data in the rtmpdump format

Additional options:
  -p PORT         RTMP port (Default: sniffs on all ports)
  --one           Quit after the first stream found
  --quiet         Doesn't print anything except the RTMP output
  --debug         Enable DEBUG mode

```

## Examples

Sniffing on all interfaces, without any filter:
```
sudo ./rtmpSnoop.py
```
