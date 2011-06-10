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
crc_regex  = re.compile(r'[^A-F0-9]([A-F0-9]{8})[^A-F0-9]', re.IGNORECASE)
colors = {
    'failed':  '\033[1;31m', # red
    'ok':      '\033[1;32m', # green
    'unknown': '\033[1;33m', # yellow
    'default': '\033[0m',
}

def crc32(fname):
    f = open(fname, 'rb')
    blksize = os.fstat(f.fileno()).st_blksize
    crc = 0
    while True:
        data = f.read(blksize)
        if not data:
            break
        crc = binascii.crc32(data, crc) & 0xffffffff
    f.close()
    return crc

def get_next_file(dirname):
    for (root, dirs, files) in os.walk(dirname):
        files.sort()
        for fname in files:
            if fname.rsplit('.')[-1].lower() in extensions:
                yield os.path.join(root, fname)

def check_file(f, cs=None):
    status, s_str = 'unknown', ''
    m = re.search(crc_regex, f)
    crc = crc32(f)
    if m and not cs:
        cs = int(m.group(1), 16)
    if cs:
        status = 'ok' if crc == cs else 'failed'
        s_str  = status.upper()
    else:
        s_str  = '%08X' % crc
    ncols = int(os.popen('stty size').read().split()[1])
    fname = f.decode('utf-8')
    pad   = ncols - len(fname) - len(s_str) - 2
    if pad <= 0:
        fname = '...' + fname[4 - pad:]
        pad = 1
    print '%s\033[%dC%s[%s]%s' % (fname, pad, colors[status], s_str, colors['default'])

def check_sfv(fname):
    p = os.path.dirname(fname)
    f = open(fname, 'r')
    for line in f:
        m = re.search('^([^#]*)\s+([A-F0-9]{8})$', line, re.IGNORECASE)
        if m is not None:
            n, c = m.group(1, 2)
            check_file(os.path.join(p, n), int(c, 16))
    f.close()


if len(sys.argv) < 2:
    print 'Usage: %s [DIR | FILE]' % sys.argv[0]
    sys.exit(1)

try:
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            for f in get_next_file(arg):
                check_file(f)
        elif arg.lower().endswith('.sfv'):
            check_sfv(arg)
        else:
            check_file(arg)
except KeyboardInterrupt:
    sys.exit(1)

