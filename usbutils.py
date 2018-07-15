import sys
if sys.platform.startswith('linux'):
    from usbutils_linux import *
elif sys.platform.startswith('win32'):
    from usbutils_win32 import *
elif sys.platform.startswith('darwin'):
    from usbutils_darwin import *

