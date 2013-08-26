#!/usr/bin/env python
"""CLI torrent creation utility."""

import os
import os.path
import sys

import sha
import datetime
import getopt

import pymktorrent
import pymktorrent.torrent
import pymktorrent.bencode

piece_length = 262144
announce = None
source = None
destination = None
comment = None

def usage():
    print "Usage: %s [OPTIONS]... <source> <destination>" % sys.argv[0]
    print
    print "Mandatory arguments to long options are mandatory",
    print "for short options too."
    print "  -a, --announce=URL         set tracker to URL"
    print "  -l, --piece_length=LEN     set piece length to LEN"
    print "  -c, --comment=COMMENT      set comment to COMMENT"
    print "  -h, --help                 display this help text"
    print "      --version              output version and exit"
    print
    print "Report bugs to <ludvig.ericson@gmail.com>."

try:
    opts, args = getopt.getopt(sys.argv[1:],
        "a:p:P:l:c:ih", ("announce=", "port=", "path=", "piecelength=",
        "comment=", "inclusive", "version", "help"))
except getopt.GetoptError, e:
    print e
    usage()
    sys.exit(1)

for opt, val in opts:
    opt = opt[1:]
    if opt in ("a", "-announce"):
        announce = val
    elif opt in "pPi" or opt in ("-port", "-path", "-inclusive"):
        pass
    elif opt in ("c", "-comment"):
        comment = val
    elif opt in ("l", "-piecelength"):
        piece_length = int(val)
    elif opt == "-version":
        print "pymktorrent " + pymktorrent.version_str()
        sys.exit(0)
    elif opt in ("h", "-help"):
        usage()
        sys.exit(0)

try:
    destination = args.pop()
    source = args.pop()
except IndexError:
    print "missing source and/or destination"
    usage()
    sys.exit(1)

if args or not announce:
    if args:
        print "excessive arguments"
    if not announce:
        print "no announcement URL provided"
    usage()
    sys.exit(1)

torrent = pymktorrent.torrent.TorrentMetaFile()

torrent.announce = announce
torrent.creation_date = datetime.datetime.now()
torrent.tree["created by"] = "pymktorrent " + pymktorrent.version_str()

torrent.name = os.path.basename(os.path.realpath(source))

pieces = pymktorrent.torrent.PieceHasher(piece_length)
if not os.path.exists(source):
    print "source does not exist"
    sys.exit(1)
elif os.path.isdir(source):
    def _walker(arg, dirname, rnames):
        torrent, pieces = arg
        names = rnames[:] # I daren't modify rnames.
        names.sort()
        for name in names:
            if name.startswith("."):
                names.remove(name)
                continue
            filepath = os.path.join(dirname, name)
            if os.path.isfile(filepath):
                path = dirname[len(source):].split(os.path.sep)
                if not path[0]:
                    path = path[1:]
                print "adding", filepath
                torrent.add_file(path, name, os.path.getsize(filepath))
                f = None
                try:
                    f = file(filepath, "rb")
                    if os.isatty(sys.stdout.fileno()):
                        sys.stdout.write("hashing...\r")
                        sys.stdout.flush()
                    pieces.consume(f)
                finally:
                    if f: f.close()
    # Not setting path to anything since that's how torrents work, the name
    # is prepended as a directory to contain all files.
    os.path.walk(source, _walker, (torrent, pieces))
else:
    f = None
    try:
        f = file(source, "rb")
        pieces.consume(f)
    finally:
        if f: f.close()

torrent.tree["info"]["piece length"] = pieces.piece_length
torrent.pieces = pieces.finalize()

if comment: torrent.tree["comment"] = comment

f = None
try:
    f = file(destination, "wb")
    f.write(torrent.encode().text)
finally:
    if f: f.close()

print "torrent name", torrent.name
print "info hash (torrent id):", torrent.get_info_hash().encode("hex")
if comment: print "torrent comment", comment
print len(torrent.pieces), "pieces written"
print pymktorrent.bytes_to_human(torrent.total_size) + "B content size"
