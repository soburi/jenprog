import os
import re
import sys

def query_iserial_linux(devname):
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

def query_iserial_windows(devname):
    import wmi
    c  = wmi.WMI(namespace='CIMV2')
    result = c.query('SELECT * FROM Win32_PnPEntity WHERE ClassGuid="{4d36e978-e325-11ce-bfc1-08002be10318}"')

    for pnp in result:
        compatt = re.compile(r'.*\((COM\d+)\).*')
        matched = re.match(compatt, pnp.Caption)
        comstr = matched.group(1)

        if devname == comstr:
            serpatt = re.compile(r'^FTDIBUS\\VID_\d{4}\+PID_\d{4}\+(\w*)A\\0000')
            matched = re.match(serpatt, pnp.DeviceID)
            if matched != None and devname == comstr:
                return matched.group(1)

    raise Exception(devname + 'Not Found')

def driver_restore_linux(vid, pid, serial):
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

def driver_restore_windows(vid, pid, serial):
    return

def query_iserial(devname):
    try:
        func = eval('query_iserial_' + sys.platform)
    except Exception as e:
        print(e)
        raise Exception('Not supported platform')
    return func(devname)

def driver_restore(vid, pid, serial):
    try:
        func = eval('driver_restore_' + sys.platform)
    except:
        raise Exception('Not supported platform')
    func(vid, pid, serial)
