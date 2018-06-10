from time import time
from sys import stdout, stderr
from os import SEEK_END, SEEK_SET
import logging

def open_bootloader(options):
    if options.conn=='serial':
        import con_serial
        return con_serial.SerialBootloader(options.target)
    elif options.conn=='ipv6':
        import con_ipv6
        return con_ipv6.IPBootloader(options.target)
    elif options.conn=='ftdi':
        import con_ftdi
        return con_ftdi.FtdiBootloader(options.target, options.initbaud, options.progbaud)
    elif options.conn=='ftd2xx':
        import con_ftd2xx
        return con_ftd2xx.Ftd2xxBootloader(options.target, options.initbaud, options.progbaud)
    elif options.conn=='raspi':
        import con_raspi
        return con_raspi.RaspiBootloader(options.target, options.initbaud, options.progbaud, options.reset, options.spimiso)
    else:
        raise Exception('nahh')

def execute(options):
    with open_bootloader(options) as bl:
        #
        # Select the actions:
        #
        if options.show or options.erase:
            stdout.write("flash: %s %s\n"%(bl.flash_manufacturer, bl.flash_type))
            stdout.write("mac: 0x")
            for b in bl.read_mac(): stdout.write("%02x"%b)
            stdout.write(" license: 0x")
            for b in bl.read_license(): stdout.write("%02x"%b)
            stdout.write("\n")
            if options.erase: bl.erase_flash()

        elif options.mac:
            bl.set_mac(options.mac)
            bl.write_mac()

        elif options.key:
            bl.set_license(options.key)
            bl.write_license()

        elif options.dump:
            block,i,start = bl.preferedblocksize or 0xf0,0,time()
            for addr in range(options.addr, options.addr+options.len, block):
                for byte in bl.read_flash(addr, block):
                    stdout.write("%c"%byte)

                if addr>((options.addr+options.len)/10.*i):
                    logging.info("%i%%.."%(i*10))
                    i += 1

            kb,sec  = options.len/1000., (time()-start)
            logging.info("done - %0.2f kb/s"%(kb/sec))

        elif options.program:
            binfile = open(options.program, "rb")

            # read the binfile size
            binfile.seek(0,SEEK_END)
            size = binfile.tell()
            binfile.seek(0,SEEK_SET)

            MAGIC = bytes([0x12, 0x34, 0x56, 0x78, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88])

            header = binfile.read(16)
            if MAGIC == header[0:12]:
                is_jn516x_format = False
            elif MAGIC == header[4:16]:
                is_jn516x_format = True
            else:
                raise Exception("unsupported binary format.")

            binfile.seek(0,SEEK_SET)

            if is_jn516x_format:
                flashtype = binfile.read(1)
                ramsize   = binfile.read(1)
                chiptype  = binfile.read(2)

            # start reading the file, 0x80 seems to be the only blocksize
            # working for the jennic bootloader with certain flashtypes
            block,i,start = bl.preferedblocksize or 0x80,0,time()
            data = binfile.read(block)
            addr = 0x00000000

            # erase_flash gets the mac and license key prior to doing
            # its opertation.
            bl.erase_flash()

            # issue a write_init command if the boot loader supports
            # that.
            if hasattr(bl, 'write_init'):
                bl.write_init(size)

            while len(data) != 0:
                if hasattr(bl, 'write2_flash'):
                    bl.write2_flash(addr, data)
                else:
                    bl.write_flash(addr, data)
                addr += len(data)
                data  = binfile.read(block)

                if addr>(size/10.*i):
                    logging.info("%i%%.."%(i*10))
                    i += 1

            kb,sec  = size/1000., (time()-start)
            logging.info("done - %0.2f kb/s "%(kb/sec))

            #logging.info("- writing mac address and key..")
            #bl.write_mac()
            #bl.write_license()
            #logging.info("done")

            #if options.verify:
            #    raise Exception("not implemented")
