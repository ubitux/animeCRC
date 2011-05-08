#!/usr/bin/env python
#
# DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                     Version 2, December 2004
#
#  Copyright (C) 2011 ubitux
#  Everyone is permitted to copy and distribute verbatim or modified
#  copies of this license document, and changing it is allowed as long
#  as the name is changed.
#
#             DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#    TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#   0. You just DO WHAT THE FUCK YOU WANT TO.
#

import os, sys, re, binascii

extensions = ('avi', 'mkv', 'mp4', 'ogm')
crc_regex  = re.compile(r'[^A-F0-9]([A-F0-9]{8})[^A-F0-9]')
colors = {
    'failed':  '\033[1;31m', # red
    'ok':      '\033[1;32m', # green
    'unknown': '\033[1;33m', # yellow
    'default': '\033[0m',
}

def crc32(fname):
    f = open(fname, 'rb')
    crc = 0
    while True:
        data = f.read(8192)
        if not data:
            break
        crc = binascii.crc32(data, crc) & 0xffffffff
    f.close()
    return crc

def get_next_file(dirname):
    for (root, dirs, files) in os.walk(dirname):
        for fname in files:
            if fname.rsplit('.')[-1].lower() in extensions:
                yield os.path.join(root, fname)

if len(sys.argv) != 2:
    print 'Usage: %s [DIR]' % sys.argv[0]
    sys.exit(1)

for f in get_next_file(sys.argv[1]):
    status = 'unknown'
    m = re.search(crc_regex, f)
    if m:
        crc = crc32(f)
        status = 'ok' if crc == int(m.group(1), 16) else 'failed'
    ncols = int(os.popen('stty size').read().split()[1])
    fname = f.decode('utf-8')
    pad   = ncols - len(fname) - len(status) - 2
    if pad < 0:
        fname = '...' + fname[-1*(pad - len('...') - 1):]
        pad = 1
    print '%s\033[%dC%s[%s]%s' % (fname, pad, colors[status], status.upper(), colors['default'])
