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
from scapy.all import hexdump

class Stream():
    
    def __init__(self, stream = ""):
        self.stream = stream
        self.offset = 0
        self.size = len(stream)
        self.dontScanAgain = False

    #Appends new data to the stream
    def appendData(self, data):
        self.stream +=data
        self.size +=len(data)
    
    #Prints the stream 
    def dump(self):
        hexdump(self.stream[self.offset:])

    #Gets n bytes from the buffer and increments the offset
    def getBytes(self, n):
        if self.offset + n> self.size:
            raise StreamNoMoreBytes

        bytes = self.stream[self.offset:self.offset+n]
        self.offset = self.offset + n
        return bytes

    #Get a single byte from the stream
    def getByte(self):
        return ord(self.getBytes(1))

    #Reads n bytes from the buffer without increments the offset
    def readBytes(self, n):
        if self.offset >= self.size:
            return None

        bytes = self.stream[self.offset:self.offset+n]
        return bytes

    #Returns True if there are bytes to be read, False otherwise
    def haveBytes(self):
        if self.offset >= self.size:
            return False
        else:
            return True

class StreamNoMoreBytes(Exception):
    pass

