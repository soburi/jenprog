import os
import re
import sys

def query_serialno_linux(devname):
    devbody = re.sub(r'^.*\/', '', devname)
    devfile = '/sys/bus/usb-serial/devices/' + devbody
    result = os.readlink(devfile)

    if result[0] != '/':
        serialinfo = os.path.join(os.path.dirname(devfile), result, '../../serial')
    else:
        serialinfo = result

    f = open(serialinfo)
    serial = f.read().strip()
    f.close()

    return serial

def query_serialno_windows(devname):
    import wmi
    c  = wmi.WMI(namespace='CIMV2')
    result = c.query('SELECT * FROM Win32_PnPEntity WHERE ClassGuid="{4d36e978-e325-11ce-bfc1-08002be10318}"')

    for pnp in result:
        compatt = re.compile(r'.*\((COM\d+)\).*')
        matched = re.match(compatt, pnp.Caption)
        if matched == None:
            continue

        comstr = matched.group(1)

        serpatt = re.compile(r'^FTDIBUS\\VID_\d{4}\+PID_\d{4}\+(\w{8}).*')
        matched = re.match(serpatt, pnp.DeviceID)
        if matched == None:
            continue

        serialnum = matched.group(1)

        if comstr == devname:
            return serialnum

    raise Exception('NotFound')

def query_serialno(devname):
    if sys.platform == 'linux':
        return query_serialno_linux(devname)
    elif sys.platform == 'win32':
        return query_serialno_windows(devname)
    else:
        raise Exception('Not supported platform')

