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
import struct
import Utils
from lib.Stream import Stream
from lib.amfCommand import amfCommand, amfCommands
from lib.Logger import logger
from scapy.all import *

class rtmpParser():

    AMF_COMMAND = 0x14
    AMF3_COMMAND = 0x11

    AMF_STRING = chr(0x02)
    AMF_NUMBER = chr(0x00)
    AMF_OBJECT = chr(0x03)
    AMF_BOOLEAN = chr(0x01)
    AMF_NULL = chr(0x05)
    AMF_ARRAY = chr(0x08)

    def __init__ (self):
        pass

    """ 
    Parses the stream packet by packet
    and returs a list containing all the amfCommand objects found """
    def rtmpParseStream (self, stream):

        amfCmds = amfCommands()
        
        #Looking for the handshake
        H1 = stream.getBytes(1)
        H1_rndData = stream.getBytes(0x600) #1536
        H2_rndData = stream.getBytes(0x600)

        if H1 != chr(0x03) or H1_rndData == None or H2_rndData == None:
            return amfCmds
    
        while (stream.haveBytes()):

            amf = self.rtmpParsePacket (stream)        

            if amf:
                amfCmds.add(amf)

        return amfCmds

    """
    Parses the RTMP object at the beginning of the stream.
    The stream pointer is incremented."""
    def rtmpParsePacket (self, stream):

        """
        Looking for the packet header
        byte 1
        BB BBBBBB
        The first 2 bit indicates the header type as following:
            b00 = 12 byte header (full header).
            b01 = 8 bytes - like type b00. not including message ID (4 last bytes).
            b10 = 4 bytes - Basic Header and timestamp (3 bytes) are included.
            b11 = 1 byte - only the Basic Header is included.

        The last 6 bit indicates the chunk stream ID
        """
        byte = stream.getByte()
        header_type = byte >> 6
        chunk_stream_id = byte << 2
        chunk_stream_id = chunk_stream_id >> 2

        #Header type b00
        if header_type == 0:
            timestamp = Utils.str2num(stream.getBytes(3))
            body_size = Utils.str2num(stream.getBytes(3))
            packet_type = stream.getByte()
            stream_id = Utils.str2num(stream.getBytes(4))
        
        #Header type b01
        elif header_type == 1:
            timestamp = Utils.str2num(stream.getBytes(3))
            body_size = Utils.str2num(stream.getBytes(3))
            packet_type = stream.getByte()

            """ 
        Header type b10 or b11
        Maybe this means that we reached the end of the stream
        with the setBufferLenght command, so simply I will set the entire stream "as readed"
        to end the parsing process """
        elif header_type == 2 or header_type == 3:
            stream.offset = stream.size
            return None

        else:
            logger.error("RTMP header type not supported: %d", header_type)
            return None

        #Now reading the RTMP payload from the stream
        magic_byte = 0xC0 + chunk_stream_id
        magic_bytes_count = body_size / 128
        rtmp_payload = stream.getBytes(body_size + magic_bytes_count)

        if rtmp_payload == None:
            return None

        #Unchunking the payload
        n = 0
        while (n<len(rtmp_payload)):
            if (n % 128 == 0) and (n != 0):
                if rtmp_payload[n] == chr(magic_byte):
                    rtmp_payload = rtmp_payload[:n] + rtmp_payload[n+1:]
                else:
                    logger.debug("Expected RTMP magic byte not found in the payload: %d" % n)
                    return None
            n = n + 1            
       
        """
        Now parsing the payload!
        I will create a new Stream object, containing only the payload, to pass to the
        parsing function """
        rtmp_payload_stream = Stream(rtmp_payload)

        #If it's an AMF/AMF3 command
        if packet_type == self.AMF_COMMAND or packet_type == self.AMF3_COMMAND:

            amf = amfCommand()

            #rtmp_payload_stream.dump()

            """ 
            In case of AMF3 command, there is an extra byte at the beginning of the body
            So, lets get it! """
            if packet_type == self.AMF3_COMMAND:
                rtmp_payload_stream.getByte()

            """
            The structure of the RTMP Command is:
                (String) <Command Name>
                (Number) <Transaction Id>
                (Mixed)  <Argument> ex. Null, String, Object: {key1:value1, key2:value2 ... }
            """

            #Reading AMF Command
            amf.name = self.rtmpParseObject(rtmp_payload_stream)

            #We are interested only in "connect" and "play" objects for our purpose
            if amf.name not in ["connect","play"]:
                logger.debug("Found an unuseful command, skypping!: %s" % amf.name)
                return None

            #Reading AMF Transaction ID
            amf.transaction_id = self.rtmpParseObject(rtmp_payload_stream)

            #Reading all the AMF arguments
            while (rtmp_payload_stream.haveBytes()):
                amf.args.append(self.rtmpParseObject(rtmp_payload_stream))

            return amf
        
        #Otherwise, I can discard it...
        else:
            logger.debug("Found an unuseful packet type, skypping!: %d" % packet_type)
            
        return None
        

    #Parse a single RTMP object
    def rtmpParseObject(self, p):

        #Object type
        b = p.getBytes(1)

        #STRING
        if (b == self.AMF_STRING):
            strlen =  Utils.str2num(p.getBytes(2))
            string = p.getBytes(strlen)
            logger.debug("Found a string [%s]..." % string)
            return string

        #NUMBER
        #Numbers are stored as 8 byte (big endian) float double
        elif (b == self.AMF_NUMBER):
            number = struct.unpack('>d',p.getBytes(8))
            logger.debug("Found a number [%d]..." % number)
            return int(number[0])

        #BOOLEAN
        elif (b == self.AMF_BOOLEAN):
            boolean = False if (p.getBytes(1) == chr(0)) else True
            logger.debug("Found a boolean (%s)..." % boolean)
            return boolean

        #OBJECT
        elif (b == self.AMF_OBJECT):
            logger.debug("Found an object...")
            obj = dict()

            #Reading all the object properties, until End Of Object marker is reached
            while (p.readBytes(3) != "\x00\x00\x09"):
                
                #Property name
                strlen =  Utils.str2num(p.getBytes(2))
                key = p.getBytes(strlen)
                logger.debug("Property name [%s]..." % key)

                #Property value
                val = self.rtmpParseObject(p)

                obj[key] = val

            #Eating the End Of Object marker
            p.getBytes(3)
            
            return obj

        #NULL
        elif (b == self.AMF_NULL):
            logger.debug("Found a NULL byte...")
            return None

        #ARRAY
        #I don't care about it...
        elif (b == self.AMF_ARRAY):
            arraylen =  Utils.str2num(p.getBytes(4))
            logger.debug("Found an array...")
            while (p.readBytes(3) != "\x00\x00\x09"):
                pass
            p.getBytes(3)
            return 0
       
        #Unknown object
        else:
            logger.error("Found an unknown RTMP object: 0x%x" % ord(b))
            return None

