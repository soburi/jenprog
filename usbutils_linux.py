import os
import re
import sys
import usb1

def query_usb_id(devname):
    devbody = re.sub(r'^.*\/', '', devname)
    devfile = '/sys/bus/usb-serial/devices/' + devbody
    result = os.readlink(devfile)

    if result[0] != '/':
        serial = os.path.join(os.path.dirname(devfile), result, '../../serial')
        vendor = os.path.join(os.path.dirname(devfile), result, '../../idVendor')
        product = os.path.join(os.path.dirname(devfile), result, '../../idProduct')
    else:
        raise Exception(devname + 'Not Found')

    f = open(serial)
    if f != None:
        iSerial = f.read().strip()
        f.close()
    f = open(vendor)
    if f != None:
        idVendor = f.read().strip()
        f.close()
    f = open(product)
    if f != None:
        idProduct = f.read().strip()
        f.close()

    if iSerial != None and idVendor != None and idProduct != None:
        return [int(idVendor,16), int(idProduct, 16), iSerial]

    raise Exception(devname + 'Not Found')

def driver_restore(vid, pid, serial):
    with usb1.USBContext() as context:
        for device in context.getDeviceIterator(skip_on_error=True):
            if device.getVendorID() == vid and device.getProductID() == pid:
                handle = device.open()
                for configuration in device.iterConfigurations():
                    for interface in configuration:
                        for setting in interface:
                            if not handle.kernelDriverActive(setting.getNumber()):
                                handle.attachKernelDriver(setting.getNumber())

