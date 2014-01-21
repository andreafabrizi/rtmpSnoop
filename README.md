# rtmpSnoop - The RTMP sniffer!

**rtmpSnoop** lets you to sniff RTMP streams from live TV, online channels and straming services and dump the RTMP properties in many formats.
You can analyse both live and dumped streams.

## Features

* Live sniffing from one ore more interfaces
* Read dumped streams from PCAP files
* Dump the RTMP properties in more formats (simple list, m3u entry or rtmpdump syntax)
* Easy to use and cross platform!

## Requirements

**rtmpSnoop** works both on Windows and Unix.  
To run it you need only python (at least 2.7 version) and the scapy module. 

**Linux Installation**  
* Debian/Ubuntu:  
`apt-get install python-scapy`

* RedHat/Centos:  
`yum install scapy.noarch`  
`yum install python-argparse.noarch`  

**Mac Installation**  

* Download pcapy from http://corelabs.coresecurity.com/
* Download dnet from http://libdnet.sourceforge.net/

Unzip and cd in to dnet file then

```
 CFLAGS='-arch i386 -arch x86_64' ./configure --prefix=/usr
 archargs='-arch i386 -arch x86_64' make
 sudo make install
 cd python
 sudo python setup.py install
```

**Windows Installation**  
Follow this guide to install scapy module on windows:
http://www.secdev.org/projects/scapy/doc/installation.html#windows

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

Sniffing on all interfaces, without filters:
```
sudo python rtmpSnoop.py
```

Sniffing on eth0, and looking for RTMP streams on port 1935 only:
```
sudo python rtmpSnoop.py -i eth0 -p 1935
```

Reading streams from PCAP file:
```
python rtmpSnoop.py -f dump/tv.pcap
```

## Output formats

Default list:
```
url: rtmp://192.168.1.1/live/channel?id=123
app: live
pageUrl: http://www.test.com/embedded/channel/1/500/380
swfUrl: http://www.test.eu/static/player.swf
tcUrl: rtmp://192.168.1.1/live
playPath: channel?id=123
flashVer: LNX 11,7,700,203
extra: S:OK 
```

m3u entry:
```
#EXTINF:0,1, Stream
rtmp://192.168.1.1/live/channel?id=12345 app=live pageUrl=http://www.test.eu/embedded/channel/1/500/380 
swfUrl=http://www.test.eu/static/player.swf tcUrl=rtmp://192.168.1.1/live playPath=channel?id=123 conn=S:OK live=1
```

rtmpdump syntax:
```
rtmpdump -r 'rtmp://192.168.1.1/live/channel?id=12345' -a 'live' -t 'rtmp://192.168.1.1/live' 
-y 'channel?id=12345' -W 'http://www.test.eu/scripts/player.swf' -p 'http://www.test.eu/embedded/channel/1/500/380' 
-f 'LNX 11,7,700,203' -C S:OK  --live -o stream.flv
```

## Donations

 If you want to support this project, please consider donating:
 * PayPal: andrea.fabrizi@gmail.com
 * BTC: 1JHCGAMpKqUwBjcT3Kno9Wd5z16K6WKPqG
