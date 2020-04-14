#!/usr/bin/env python3
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.
#

import os, sys, re, binascii
import os.path as op

extensions = ('avi', 'mkv', 'mp4', 'ogm')
crc_regex  = re.compile(r'[^A-F0-9]([A-F0-9]{8})[^A-F0-9]', re.IGNORECASE)
colors = {
    'failed':  '\033[1;31m', # red
    'ok':      '\033[1;32m', # green
    'unknown': '\033[1;33m', # yellow
    'pg':      '\033[1;34m', # blue
    'default': '\033[0m',
}

def _print_status(fname, clr, st, end='\n'):
    ncols = int(os.popen('stty size').read().split()[1])
    st    = '[%s]' % st
    pad   = ncols - len(fname) - len(st)
    if pad <= 0:
        fname = '...' + fname[4 - pad:]
        pad = 1
    sys.stdout.write(fname + ' '*pad + colors[clr] + st + colors['default'] + end)

def _crc32(fname):
    f = open(fname, 'rb')
    blksize = 1<<20
    fsize = os.fstat(f.fileno()).st_size
    crc = 0
    for size in range(0, fsize, blksize):
        data = f.read(blksize)
        crc = binascii.crc32(data, crc) & 0xffffffff
        _print_status(fname, 'pg', '%2d%%' % (size * 100 / fsize), end='\r')
    f.close()
    return crc

def _get_next_file(dirname):
    for (root, dirs, files) in os.walk(dirname):
        files.sort()
        for fname in files:
            if fname.rsplit('.')[-1].lower() in extensions:
                yield op.join(root, fname)

def _check_file(f, cs=None):
    status, s_str = 'unknown', ''
    m = re.search(crc_regex, f)
    crc = _crc32(f)
    if m and not cs:
        cs = int(m.group(1), 16)
    if cs:
        status = 'ok' if crc == cs else 'failed'
        s_str  = status.upper()
    else:
        s_str  = '%08X' % crc
    _print_status(f, status, s_str)

def _check_sfv(fname):
    p = op.dirname(fname)
    f = open(fname, 'r')
    for line in f:
        m = re.search('^([^;]*\S+)\s+([A-F0-9]{8})$', line.strip(), re.IGNORECASE)
        if m is not None:
            n, c = m.group(1, 2)
            _check_file(op.join(p, n), int(c, 16))
    f.close()


def _main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} [DIR | FILE]')
        sys.exit(1)

    try:
        for arg in sys.argv[1:]:
            if op.isdir(arg):
                for f in _get_next_file(arg):
                    _check_file(f)
            elif arg.lower().endswith('.sfv'):
                _check_sfv(arg)
            else:
                _check_file(arg)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    _main()
