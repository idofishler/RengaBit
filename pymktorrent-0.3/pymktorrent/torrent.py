#!/usr/bin/env python

import time
import datetime
import sha

import pymktorrent
import pymktorrent.bencode

class TorrentMetaFile(object):
    _merge_keys = "announce", "creation date", "encoding", "created_by"

    def __init__(self, data=None):
        self.tree = {"info": {}}
        self.pieces = []
        self.encoding = "utf-8" 
        self.total_size = 0
        if data:
            self.decode(data)

    def decode(self, data):
        # We just take the first "root" level element since the torrent
        # "standard" says that the first one is the only one that is
        # in fact relevant to the metadata, and has to be a dict too.
        self.tree.update(pymktorrent.bencode.BDecoder(data).stack[0])

        for mk in self._merge_keys:
            try:
                if mk == "creation date":
                    self.creation_date = datetime.datetime(
                        *time.localtime(self.tree[mk])[:-2])
                else:
                    setattr(self, mk, self.tree[mk])
            except KeyError:
                # If the torrent doesn't have it, we don't care.
                pass

        try:
            self.name = self.tree["info"]["name"].decode(self.encoding)
        except LookupError:
            self.name = self.tree["info"]["name"]
        except KeyError:
            raise pymktorrent.TorrentFormatError("torrent has no name")

        if "files" in self.tree["info"]:
            for f in self.tree["info"]["files"]:
                self.total_size += int(f["length"])
        elif "length" in self.tree["info"]:
            self.total_size = int(self.tree["info"]["length"])
        else:
            raise pymktorrent.TorrentFormatError(
                "no files list nor length integer")

        if len(self.tree["info"]["pieces"]) % 20:
            raise pymktorrent.TorrentFormatError(
                "the pieces' hash field isn't a multiple of 20")

        for x in xrange(len(self.tree["info"]["pieces"]) / 20):
            self.pieces.append(self.tree["info"]["pieces"][x * 20:x * 20 + 20])

        if self.total_size / float(
           self.tree["info"]["piece length"]) > len(self.pieces):
            raise pymktorrent.TorrentFormatError(
                "there are less piece-hashes than there are theoretical " +
                "pieces")

    def get_info_hash(self):
        return sha.sha(pymktorrent.bencode.BEncoder(
            self.tree["info"]).text).digest()
    
    def encode(self):
        tree = self.tree.copy()
        for mk in self._merge_keys:
            try:
                tree[mk] = getattr(self, mk)
            except AttributeError:
                pass
        tree["creation date"] = int(
            time.mktime(self.creation_date.timetuple()))
        # Note: We /have/ to do this otherwise we end up with weird
        # str types (unicode) that will cause fatal AIDS and stuff.
        tree["info"]["name"] = self.name.encode(self.encoding)
        tree["info"]["pieces"] = "".join(self.pieces)
        return pymktorrent.bencode.BEncoder(tree)

    def add_file(self, path, name, size):
        if "info" not in self.tree:
            self.tree["info"] = {"files": []}
        elif "files" not in self.tree["info"]:
            self.tree["info"]["files"] = []

        self.tree["info"]["files"].append({
            "length": size,
            "path": path[:] + [name]
        })

        self.total_size += size

class PieceHasher(object):
    def __init__(self, piece_length):
        self.piece_length = piece_length
        self.pieces = []
        self.hash_buffer = ""

    def consume(self, f):
        data = True
        pc = 0
        while data:
            data = f.read(self.piece_length - len(self.hash_buffer))
            self.hash_buffer += data
            if self.piece_length == len(self.hash_buffer):
                self._piece_push()
                pc += 1
        return pc

    def finalize(self):
        self._piece_push()
        return self.pieces

    def _piece_push(self):
        self.pieces.append(sha.sha(self.hash_buffer).digest())
        self.hash_buffer = ""
