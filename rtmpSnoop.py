#!/usr/bin/env python
#
# This module is part of the rtmpSnoop project
#  https://github.com/andreafabrizi/rtmpSnoop
#
# Copyright (C) 2013 Andrea Fabrizi <andrea.fabrizi@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 3 of
# the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA
#
import os
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from lib.Stream import *
from lib.rtmpParser import rtmpParser
from lib.amfCommand import amfCommand, amfCommands
from lib.Logger import logger
import argparse

VERSION="0.2"

"""
Packet Handler Callback from scapy
I don't care about the packet fragmentation, because is supposed that I'm sniffing on
a local interface, so shouldn't be a packet fragmentation problem.

"""
def PacketHandler(pkt):

    global streams
    global rtmp_port
    global out_mode
    global quit_first

    if pkt.haslayer(TCP) and pkt.haslayer(Raw):

        #Skipping if the rtmp_port is defined and is different from the packet dest port
        if rtmp_port != 0 and pkt[TCP].dport != rtmp_port:
            return

        sport = pkt[TCP].sport
        
        #hexdump(pkt.load)

        """
        The easiest way to follow the TCP streams is to use the source port as
        distinction element. So i will consider each packet with the same source
        port as part of the same TCP stream """
        if sport not in streams:
            stream = Stream(pkt.load)
            streams[sport] = stream
        else:
            streams[sport].appendData(pkt.load)

        if streams[sport].dontScanAgain:
            return
        
        #This is the mininium size that an RTMP stream must have to contains interesting data...
        if streams[sport].size > 0x600*2:
            logger.debug("Dissecting stream: %s" % sport)

            rtmp = rtmpParser()

            try:
                amfCmds = rtmp.rtmpParseStream(streams[sport])

                #If I have 2 AMF commands (play and connect), I can print the results
                if amfCmds.count() == 2:
                    logger.info("\n* RTMP Stream found!")
                    amfCmds.printOut(out_mode)
                    streams[sport].dontScanAgain = True
                    if quit_first:
                        sys.exit(0)
                else:
                    streams[sport].offset = 0

            except StreamNoMoreBytes:
                logger.debug("No more bytes to read from the stream!")

            except Exception as e:
                logger.error("Error parsing the RTMP stream: %s" % e)


"""
Setting up the argparse and usage """
def setupArgParser():

    parser = argparse.ArgumentParser(description="rtmpSnoop lets you to grab the RTMP properties from live or dumped streams.")

    group_input = parser.add_argument_group("Input")
    group = group_input.add_mutually_exclusive_group()
    group.add_argument("-i", action="store", dest="device", help="Device to sniff on (Default: sniffs on all devices)")
    group.add_argument("-f", action="store", dest="pcapfile", help="PCAP file to read from")

    group_output = parser.add_argument_group("Output format")
    group = group_output.add_mutually_exclusive_group()
    group.add_argument("--out-list", action='store_const', const="list", dest="out_mode", help="Prints the RTMP data as list (Default)")
    group.add_argument("--out-m3u", action='store_const', const="m3u", dest="out_mode", help="Prints the RTMP data as m3u entry")
    group.add_argument("--out-rtmpdump", action='store_const', const="rtmpdump", dest="out_mode", help="Prints the RTMP data in the rtmpdump format")

    group_input = parser.add_argument_group("Additional options")
    group_input.add_argument("-p", action="store", dest="port", default=0, type=int, help="RTMP port (Default: sniffs on all ports)")
    group_input.add_argument("--one", action="store_true", dest="quit_first", help="Quit after the first stream found")
    group_input.add_argument("--quiet", action="store_true", help="Doesn't print anything except the RTMP output")
    group_input.add_argument("--debug", action="store_true", help="Enable DEBUG mode")

    args = parser.parse_args()

    return args

#MAIN
if __name__ == "__main__":
    
    args = setupArgParser()
    
    if args.debug:
        logger.DEBUG = True

    if args.quiet:
        logger.QUIET = True

    rtmp_port = args.port
    out_mode = args.out_mode
    quit_first = args.quit_first

    logger.info("rtmpSnoop v%s - The RTMP Sniffer!" % VERSION)
    logger.info("Andrea Fabrizi - andrea.fabrizi@gmail.com\n")

    streams = dict()

    #Not sniffing, reading from dump file
    if args.pcapfile:
        logger.info("Reading packets from dump file '%s'..." % args.pcapfile)
        sniff(offline=args.pcapfile, filter="tcp", prn = PacketHandler)

    #Sniffing on the specified device
    elif args.device:
        logger.info("Starting sniffing on %s..." % args.device)
        try:
            sniff(iface=args.device, prn = PacketHandler)
        except socket.error as e:
            logger.error("Error opening %s for sniffing: %s" % (args.device, e))
            logger.info("Are you root and the device is correct?")
            sys.exit(1)

    #Default action, sniffing on all the devices
    else:
        logger.info("Starting sniffing on all devices...")
        try:
            sniff(prn = PacketHandler)
        except socket.error as e:
            logger.error("Error opening device for sniffing: %s" % e)
            logger.info("Are you root?")
            sys.exit(1)
    


