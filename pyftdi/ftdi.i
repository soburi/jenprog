%module ftdi
%{
#include "ftdi.h"
#include <future.h>

int ftdi_write_data_async(struct ftdi_context *ftdi, unsigned char *buf, int size) { return 0; }
void ftdi_async_complete(struct ftdi_context *ftdi, int wait_for_more) {}

%}

%include "typemaps.i"
%include "carrays.i"
%array_class(unsigned char, cArray);
%apply unsigned short *OUTPUT { unsigned short *};
%apply unsigned int   *OUTPUT { unsigned int  *};

%include ftdi.h
