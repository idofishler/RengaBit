"""
Does bencoding. Hard.
"""

class BDecoder(object):
    def __init__(self, data):
        self.stack = [[]]
        self.container = self.stack[0]
        self.dk_stack = [] # dict key stack
        self.current_dk = None # Not really needed.
        in_int = False # Determines if we're i..<here>..e
        cleft = 0  # Keeps track of no. of bytes left in byte seq
        tclen = "" # Stores the decimal repr. of the length of future string.
        cdata = "" # Keeps track of either int or byte seq
        for c in data:
            if cleft:
                cdata += c
                cleft -= 1
                if not cleft:
                    self.str_data(cdata)
                    cdata = ""
            elif in_int:
                if c == "e":
                    self.int_data(int(cdata))
                    cdata = ""
                    in_int = False
                else:
                    cdata += c
            elif c == "d":
                self.dict_start()
            elif c == "l":
                self.list_start()
            elif c == "i":
                in_int = True
            elif c == ":":
                cleft = int(tclen)
                tclen = ""
            elif c == "e":
                self.node_ended()
            else:
                tclen += c
        # Notice now that we actually don't care about the order of dict items
        # which breaks the "standard," instead we sort it later to comply. >:)
        #
        # That also means that we spit out the dicts with an invalid order,
        # since python orders them by hash or something.
        #
        # So when you want to get a dict, do d.keys() and sort it with l.sort.

    def dict_start(self):
        self.container = dict()
        self.stack.append(self.container)
        # When a new dict starts, there's no predefined dictionary key,
        # and hence we reset the state here but keep any old one on the
        # dk stack.
        self.current_dk = None
    
    def list_start(self):
        self.container = list()
        self.stack.append(self.container)

    def general_data(self, value):
        if self.container.__class__ == list:
            self.container.append(value)
        elif self.container.__class__ == dict:
            key = self.dk_stack.pop()
            self.container[key] = value
            self.current_dk = None

    int_data = general_data

    def str_data(self, value):
        if self.container.__class__ == dict and \
           self.current_dk is None:
            self.dk_stack.append(value)
            self.current_dk = value
        else:
            self.general_data(value)
    
    def node_ended(self):
        container = self.stack.pop()
        self.container = self.stack[-1]
        self.general_data(container)

class BEncoder(object):
    def __init__(self, base):
        self.text = self.encode(base)

    def encode(self, val):
        if val.__class__ not in (int, long, str, unicode, dict, list):
            raise TypeError("can't encode object of type %r" % val.__class__)
        r = ""
        if val.__class__ is dict:
            r += "d"
            t = val.keys()
            t.sort()
            for k in t:
                r += "".join((self.encode(str(k)), self.encode(val[k])))
            r += "e"
        elif val.__class__ is list:
            r += "l"
            for i in val:
                r += self.encode(i)
            r += "e"
        elif val.__class__ in (int, long):
            r += "i%de" % (val,)
        elif val.__class__ in (str, unicode):
            r += "%d:%s" % (len(val), val)
        return r
