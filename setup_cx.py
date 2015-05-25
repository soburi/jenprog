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


from cx_Freeze import setup, Executable
from distutils.core import Extension, Command
from distutils.util import get_platform
import os
import sys
import subprocess

dep_search_path = sys.path
dep_search_path.append(os.getcwd() + '/pyftdi')
dep_search_path.append(os.getcwd() + "/build/lib.%s-%s" % (get_platform(), sys.version[0:3]) )

if not 'LIBFTDI_INCDIR' in os.environ:
    cmdout = subprocess.check_output(['pkg-config', 'libftdi', '--cflags-only-I'])
    cflags = cmdout.decode('utf-8').strip().split(' ')
    if len(cflags) == 0:
        cflags = ['-I/usr/local/include', '-I/usr/include']

    cmdout = subprocess.check_output(['pkg-config', 'libftdi', '--libs-only-L'])
    libdirs = cmdout.decode('utf-8').strip().replace('-L','').split(' ')
    if len(libdirs) == 0:
        libdirs = ['/usr/local/lib', '/usr/lib']

    cmdout = subprocess.check_output(['pkg-config', 'libftdi', '--libs-only-l'])
    libs = cmdout.decode('utf-8').strip().replace('-l','').split(' ')

else:
    cflags = []
    libdirs= []
    if 'LIBFTDI_INCDIR' in os.environ:
        cflags.append('-I' + os.environ['LIBFTDI_INCDIR'])
    if 'LIBFTDI_LIBDIR' in os.environ:
        libdirs.append(os.environ['LIBFTDI_LIBDIR'])
    if 'LIBFTDI_BINDIR' in os.environ:
        dep_search_path.append(os.environ['LIBFTDI_BINDIR'])
    if 'LIBFTD2XX_BINDIR' in os.environ:
        dep_search_path.append(os.environ['LIBFTD2XX_BINDIR'])

    libs = ['ftdi']

incdirs = list([x.replace('-I','') for x in cflags])
incdirs.append('pyftdi')

setup(name='jenprog',
      version='1.1',
      author='Philipp Scholl',
      author_email='scholl@teco.edu',
      url='http://www.teco.edu/~scholl/ba-toolchain/jenprog-1.1.tar.gz',
      py_modules=['con_ftdi', 'con_serial', 'con_ipv6', 'flashutils'],
      scripts=['jenprog'],
      ext_modules=[Extension('_ftdi', ['pyftdi/ftdi.i'],
                             swig_opts=cflags,
                             include_dirs=incdirs,
                             library_dirs=libdirs,
                             libraries=libs,
                            )],
      executables = [Executable("jenprog")],
      options = { "build_exe":
                  {
                    "bin_path_includes": dep_search_path
                  }
                },
      requires=('pyserial'))
