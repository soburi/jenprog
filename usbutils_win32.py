import os
import re
import sys

def query_usb_id(devname):
    import wmi
    c  = wmi.WMI(namespace='CIMV2')
    result = c.query('SELECT * FROM Win32_PnPEntity WHERE ClassGuid="{4d36e978-e325-11ce-bfc1-08002be10318}"')

    for pnp in result:
        compatt = re.compile(r'.*\((COM\d+)\).*')
        matched = re.match(compatt, pnp.Caption)
        comstr = matched.group(1)

        if devname == comstr:
            serpatt = re.compile(r'^FTDIBUS\\VID_(\d{4})\+PID_(\d{4})\+(\w*)A\\0000')
            matched = re.match(serpatt, pnp.DeviceID)
            if matched != None and devname == comstr:
                return [int(matched.group(1), 16), int(matched.group(2),16), matched.group(3)]

    raise Exception(devname + 'Not Found')

def driver_restore(vid, pid, serial):
    return
