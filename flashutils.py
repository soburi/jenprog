# Copyright (c) 2011
# Telecooperation Office (TecO), Universitaet Karlsruhe (TH), Germany.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
# 3. Neither the name of the Universitaet Karlsruhe (TH) nor the names
#    of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# Author(s): Philipp Scholl <scholl@teco.edu>

import sys
import logging

FLASH_ERASE       = 0x07
FLASH_PROGRAM     = 0x09
FLASH_READ        = 0x0B
SECTOR_ERASE      = 0x0D  # not use
WRITE_SR          = 0x0F  # not use
RAM_WRITE         = 0x1D  # not use
RAM_READ          = 0x1F
RUN               = 0x21
READ_FLASH_ID     = 0x25
CHANGE_BAUD_RATE  = 0x27
SELECT_FLASH_TYPE = 0x2C
GET_CHIP_ID       = 0x32

class JennicProtocol:
    def __init__(self):
        self.mac_region    = list(range(0x00000030, 0x00000038))
        self.mac_region_jn516x    = list(range(0x01001570, 0x01001578))
        self.cust_mac_region_jn516x  = list(range(0x01001580, 0x01001588))
        self.lic_region    = list(range(0x00000038, 0x00000048))
        self.mac, self.lic = None, None
        self.preferedblocksize = None

    def start(self):
        self.select_flash()
        self.identify_chip()

    def identify_chip(self):
        logging.info("identify chip")
        chipid = self.talk(GET_CHIP_ID)
        self.chipid_status = chipid[0]
        self.chipid = chipid[1]
        logging.info("chipid=%x"%chipid[1])

    def select_flash(self):
        self.identify_flash()
        if not self.flash_jennicid in (0x00, 0x01, 0x02, 0x03, 0x08):
            logging.error("unsupported flash type")
            sys.exit(1)
        status = self.talk(SELECT_FLASH_TYPE, data = [self.flash_jennicid])[0]
        if not status == 0:
            logging.error("could not select detected flash type was: %d"%status)
            sys.exit(1)

    def identify_flash(self):
        logging.info("identify flash")
        flash = self.talk(READ_FLASH_ID)
        self.flash_status       = flash[0]
        self.flash_manufacturer = flash[1]
        self.flash_type         = flash[2]

        if not self.flash_status == 0:
            logging.info("flash status != 0 (%c)"%self.flash_status)
            sys.exit(0)

        if self.flash_manufacturer == 0x10 and self.flash_type == 0x10:
            self.flash_manufacturer = "ST"
            self.flash_type         = "M25P10-A"
            self.flash_jennicid     = 0x00
        elif self.flash_manufacturer == 0xBF and self.flash_type == 0x49:
            self.flash_manufacturer = "SST"
            self.flash_type         = "25VF010A"
            self.flash_jennicid     = 0x01
        elif self.flash_manufacturer == 0x1f and (self.flash_type == 0x60\
             or self.flash_type == 0x65):
            self.flash_manufacturer = "Atmel"
            self.flash_type         = "25F512"
            self.flash_jennicid     = 0x02
        elif self.flash_manufacturer == 0x12 and self.flash_type == 0x12:
            self.flash_manufacturer = "ST"
            self.flash_type         = "M25P40"
            self.flash_jennicid     = 0x03
        elif self.flash_manufacturer == 0xCC and self.flash_type == 0xEE:
            self.flash_manufacturer = "JN516x"
            self.flash_type         = "Internal"
            self.flash_jennicid     = 0x08
        else:
            self.flash_manufacturer = "unknown"
            self.flash_type         = "unknown"
            self.flash_jennicid     = 0xFF

        logging.info("manufacturer: %s, type: %s, jennicid = 0x%x" % (self.flash_manufacturer,
             self.flash_type, self.flash_jennicid))

    def crc(self, arr, len):
        """ calculates the crc
        """
        crc = 0
        for i in range(0,len):
            crc ^= arr[i]
        return crc

    def set_mac(self, s):
        self.mac = []

        for i in range(0, len(s), 2):
            if s[i:i+2] != "0x":
                self.mac.append( int( s[i:i+2], 16 ) )

        if not len(self.mac)==len(self.mac_region):
            logging.error("mac must be %i byte long"%len(self.mac_region))
            sys.exit(1)

    def set_license(self, s):
        self.lic = []

        for i in range(0, len(s), 2):
            if s[i:i+2] != "0x":
                self.lic.append( int( s[i:i+2], 16 ) )

        if not len(self.lic)==len(self.lic_region):
            logging.error("license must be %i byte long"%len(self.lic_region))
            sys.exit(1)

    def erase_flash(self):
        """ read mac and license key prior to erasing
        """
        if not self.mac:
            self.mac = self.read_mac()
        if not self.lic:
            self.lic = self.read_license()
        #assert len(self.mac)==len(self.mac_region), "read mac addr too short"
        #assert len(self.lic)==len(self.lic_region), "read license too short"

        #if not self.talk( 0x0F, 0x10, data=[0x00] )[0] == 0:
        #    print("disabling write protection failed")
        #    sys.exit(1)

        if not self.talk(FLASH_ERASE)[0] == 0:
            logging.error("erasing did not work")
            sys.exit(1)

    def read_mac(self):
        return self.read_flash(self.mac_region[0], len(self.mac_region))

    def read_mac_jn516x(self):
        return self.read_ram(self.mac_region_jn516x[0], 8)

    def read_cust_mac_jn516x(self):
        return self.read_ram(self.cust_mac_region_jn516x[0], 8)

    def read_license(self):
        return self.read_flash(self.lic_region[0], len(self.lic_region))

    def write_license(self):
        self.write_flash(self.lic_region[0], self.lic)

    def write_mac(self):
        self.write_flash(self.mac_region[0], self.mac)

    def write_flash(self, addr, clist):
        status = self.talk(FLASH_PROGRAM, addr, data=clist)

        if status[0] != 0:
            raise Exception("writing failed for addr %i status=%i len=%i"%(addr, status[0], len(status)))

    def read_flash(self, addr, dlen):
        """ reads len bytes starting at address addr from
        flash memory.
        """
        return self.talk(FLASH_READ, addr, dlen )[1:] # strip command status

    def read_ram(self, addr, dlen):
        """ reads len bytes starting at address addr from
        ram.
        """
        return self.talk(RAM_READ, addr, dlen )[1:] # strip command status

    def finish(self):
        pass

    def baud_to_div(self, baud):
        div = 1

        while (1000000/div) > baud:
            div = div+1

        return div
