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
import os, sys

class Logger():
    def __init__ (self, debug=False, quiet=False):
        self.DEBUG = debug
        self.QUIET = quiet

    def debug(self, message):
        if self.DEBUG and not self.QUIET:
            print >> sys.stderr, "# %s" % message

    def error(self, message):
        print >> sys.stderr, "*** %s" % message

    def info(self, message):
        if not self.QUIET:
            print >> sys.stderr, message


logger = Logger()
