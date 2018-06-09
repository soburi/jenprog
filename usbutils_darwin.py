import os
import re
import sys

def query_usb_id(devname):
    import usb.core
    idev = -1

    serial = re.sub(r'^.*-', '', devname)

    # find our device
    dev = usb.core.find(find_all=True)
    if dev is not None:
        for d in dev:
            if d.serial_number == serial:
                idev = d.address
                idVendor = d.idVendor
                idProduct = d.idProduct
                iSerial = serial
                break

    if iSerial != None and idVendor != None and idProduct != None:
        return [idVendor, idProduct, iSerial]

    raise Exception(devname + 'Not Found')

def driver_restore(vid, pid, serial):
    return 0
