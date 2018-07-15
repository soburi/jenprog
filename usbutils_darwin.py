import os
import re
import sys
import usb1

def query_usb_id(devname):
    idev = -1

    serial = re.sub(r'^.*-', '', devname)

    # find our device
    with usb1.USBContext() as context:
        for device in context.getDeviceIterator(skip_on_error=True):
            if device.getSerialNumber() == serial and device.getSerialNumber() != None:
                idev = device.getDeviceAddress()
                idVendor = device.getVendorID()
                idProduct = device.getProductID()
                iSerial = serial
                break

    if iSerial != None and idVendor != None and idProduct != None:
        return [idVendor, idProduct, iSerial]

    raise Exception(devname + 'Not Found')

def driver_restore(vid, pid, serial):
    return 0
