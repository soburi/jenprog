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


import ftdi1
from time import sleep
from flashutils import JennicProtocol, CHANGE_BAUD_RATE
import logging
import sys
if sys.platform.startswith('linux'):
    import usbutils_linux as usbutils
elif sys.platform.startswith('win32'):
    import usbutils_win32 as usbutils

class Closure:
    def __init__(self, arg, func):
        self.arg = arg
        self.func = func

    def __call__(self, *args):
        ret = self.func(self.arg, *args)
        if isinstance(ret, list):
            val = ret[0]
        else:
            val = ret

        if val < 0:
            raise Exception("%s: %d"%(ftdi1.get_error_string(self.arg), val))
        else:
            return ret

class Ftdi:
    def __init__(self):
        self.context = ftdi1.new()

    def __del__(self):
        ftdi1.free(self.context)

    def __call__(self, *args):
        print(args)

    def __getattr__(self, name):
        return Closure(self.context, eval("ftdi1.%s"%name))

class FtdiBootloader(JennicProtocol):
    # use bitbang mode to jump into programming mode, see
    # enterprogrammingmode
    def __init__(self, device=None, initbaud=38400, progbaud=1000000):
        self.f = Ftdi()
        self.INITBAUD, self.PROGBAUD = int(initbaud), int(progbaud)
        self.VID, self.PID, self.SERIAL = usbutils.query_usb_id(device)
        JennicProtocol.__init__(self)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.finish()
        return False

    def start(self):
        self.f.usb_open_desc(self.VID, self.PID, None, self.SERIAL)

        self.enterprogrammingmode()
        self.doreset = 1

        self.f.set_baudrate(self.INITBAUD)
        self.f.set_line_property(ftdi1.BITS_8, ftdi1.STOP_BIT_1, ftdi1.NONE)
        self.f.setrts(1)
        self.f.setflowctrl(ftdi1.SIO_RTS_CTS_HS)
        self.f.setrts(0)

        self.f.usb_purge_buffers()

        self.talk(CHANGE_BAUD_RATE, data=[1])
        self.f.set_baudrate(self.PROGBAUD)
        super().start()

    def enterprogrammingmode(self):
        """ uses bitbang mode to set CBUS3, CBUS2 which are connected to the
        reset and programming pin on the  reference design JN-RD-6021.

        CBUS3 is connected to SPIMISO
        CBUS2 is connected to RESET
        """
        self.f.set_bitmode(0xF3, ftdi1.BITMODE_CBUS);
        sleep(.05)
        self.f.set_bitmode(0xF7, ftdi1.BITMODE_CBUS);
        sleep(.05)
        self.f.set_bitmode(0xFF, ftdi1.BITMODE_CBUS);
        sleep(.05)
        self.f.disable_bitbang()
        sleep(.05)

    def talk(self, msg_type, addr=None, mlen=None, data=None):
        """ executes one speak-reply cycle

        type     msg type prefix
        ans_type anticipiated reply type prefix
        addr     flash address for types supporting it
        mlen     number of bytes read from addr to addr+mlen
        data     array containing data to be sent

        throws an exception if the answer type is not the anticipiated one
        """
        ans_type = msg_type + 1
        msg_len = 3          # default len if no args are supplied

        if addr != None:
            msg_len += 4
        if mlen != None:
            msg_len += 2
        if data != None:
            msg_len += len(data)

        assert msg_len < 0xFF, "oversized msg, max is 256 bytes, yours is %i"%msg_len

        # pack optional args in
        msg    = [0 for i in range(msg_len) ]
        msg[0] = msg_len-1
        msg[1] = msg_type
        i      = 2

        if addr != None:
            msg[i]   =  addr& 0x000000FF
            msg[i+1] = (addr& 0x0000FF00)>>8
            msg[i+2] = (addr& 0x00FF0000)>>16
            msg[i+3] =  addr>> 24
            i       += 4
        if mlen != None:
            msg[i]   =  mlen & 0x00FF
            msg[i+1] = (mlen & 0xFF00)>>8
            i       += 2
        if data != None:
            for d in data:
                try:
                    msg[i] = d
                except TypeError:
                    msg[i] = ord(d)
                i     += 1

        # add crc
        msg[i] = self.crc(msg, msg_len-1).to_bytes(1, byteorder='little')[0]
        assert msg[i] == self.crc(msg, msg_len-1), "%i != %i"%(msg[i], self.crc(msg, msg_len))

        str = ""
        for i in range(0,msg_len):
            str += "0x%x "%msg[i]

        logging.debug(str)

        # construct answer storage
        if ans_type != None:
            ans_len = 0

            # send the message until there is an answer
            while ans_len == 0:
                waited = 0
                self.f.write_data(bytes(msg))

                # wait some cycles until the message will be repeated
                while waited < 150 and ans_len == 0:
                    ans_len, ans = self.f.read_data(1)
                    waited  += 1

            # okay we received the first byte of the answer,
            # which contains the length of the answer
            ans_len = ans[0]

            # now read the answer
            read_len, ans = self.f.read_data(ans_len)
            assert read_len == ans_len, "%i != %i" % (read_len, ans_len)
            assert ans[0] == ans_type, "recvd: 0x%x, anticipiated: 0x%x" %( ans[0], ans_type )

            arr = []
            for i in range(1, ans_len-1): # skip length and crc field
                arr.append( ans[i] )
            ans_len=0

            return arr
        else:
            self.f.write_data(msg, msg_len)

    def finish(self):
        """ depending on the connected device, do a reset.
        Switch to bitbang and toggle reset line.
        """
        if self.doreset:
            self.f.set_bitmode(0xFB, ftdi1.BITMODE_CBUS);
            sleep(.1)
            self.f.set_bitmode(0xFF, ftdi1.BITMODE_CBUS);
            sleep(.1)
            self.f.disable_bitbang()

        self.f.usb_close()
        usbutils.driver_restore(self.VID, self.PID, self.SERIAL)

