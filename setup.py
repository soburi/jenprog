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


from setuptools import setup
import sys

install_requires=['pyserial', 'ctypesftdi1', 'ftd2xx', 'libusb1']
requires=['pyserial', 'ctypesftdi1', 'ftd2xx', 'libusb1']

if sys.platform.startswith('win32'):
    reqiures.append('wmi')
    install_reqiures.append('wmi')


setup(name='jenprog',
      version='1.1',
      author='Philipp Scholl',
      author_email='scholl@teco.edu',
      url='http://www.teco.edu/~scholl/ba-toolchain/jenprog-1.1.tar.gz',
      py_modules=[ 'con_ftdi',
                   'con_serial',
                   'con_ipv6',
                   'con_ftd2xx',
                   'con_raspi',
                   'flashutils',
                   'jennic_bootloader',
                   'usbutils',
                   'usbutils_darwin',
                   'usbutils_linux',
                   'usbutils_win32', ],
      scripts=['jenprog', 'JennicModuleProgrammer'],
      requires=requires,
      install_requires=install_requires,
      )
