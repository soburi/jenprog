import os
import re
import sys

def query_iserial(devname):
    devbody = re.sub(r'^.*\/', '', devname)
    devfile = '/sys/bus/usb-serial/devices/' + devbody
    result = os.readlink(devfile)

    if result[0] != '/':
        serialinfo = os.path.join(os.path.dirname(devfile), result, '../../serial')
    else:
        serialinfo = result

    f = open(serialinfo)
    if f != None:
        iserial = f.read().strip()
        f.close()
        return iserial

    raise Exception(devname + 'Not Found')

def driver_restore(vid, pid, serial):
    import usb1
    with usb1.USBContext() as context:
        for device in context.getDeviceIterator(skip_on_error=True):
            if device.getVendorID() == vid and device.getProductID() == pid:
                handle = device.open()
                for configuration in device.iterConfigurations():
                    for interface in configuration:
                        for setting in interface:
                            if not handle.kernelDriverActive(setting.getNumber()):
                                handle.attachKernelDriver(setting.getNumber())

