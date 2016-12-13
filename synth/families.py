
import json, struct

class Target(object):
    def __init__(self, di, lo, instrs):
        self.def_in = di
        self.live_out = lo
        self.instrs = instrs
    def __str__(self):
        return "(" + ",".join(self.def_in) +")->("+",".join(self.live_out)+") {" + "; ".join(self.instrs) + "}"
    def size(self): return len(self.instrs)

class Family(object):
    def __init__(self, target):
        self.head = target
        self.rest = []
    def __str__(self):
        return str(self.head) + " & " + ",".join(map(str,self.rest))
    def merge_if_contained(self, target):
        if self.head.def_in != target.def_in:
            return False
        s = len(self.head.instrs)
        if s == len(target.instrs) and self.head.instrs == target.instrs:
            # target is the same as head. ignore so we don't get duplicates
            return True
        elif s < len(target.instrs) and self.head.instrs == target.instrs[:s]:
            self.rest.append((s,self.head.live_out))
            self.head = target
            return True
        elif s > len(target.instrs) and target.instrs == self.head.instrs[:len(target.instrs)]:
            self.rest.append((len(target.instrs), target.live_out))
            self.rest.sort(key = lambda x: x[0])
            return True
        else:
            return False

class FamilyEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, Family):
             return {"head": self.default(obj.head),"rest":obj.rest}
         elif isinstance(obj, Target):
             return [obj.def_in, obj.live_out, obj.instrs]

def save_families(families, fname):
    f = open(fname, "w")
    n = len(families)
    positions = bytearray(4*(n+2))
    f.write(positions)
    struct.pack_into("=I",positions, 0, n)
    assert f.tell() == 4*(n+2)
    for i,fam in enumerate(families):
        struct.pack_into("=I",positions, 4+4*i, f.tell())
        json.dump(fam, f, cls=FamilyEncoder)
    
    struct.pack_into("=I",positions, 4+4*n, f.tell())
    f.seek(0)
    f.write(positions)
    f.close()

def _decoder(j):
    h = j['head']
    family = Family(Target(h[0], h[1], h[2]))
    family.rest = [(x[0],x[1]) for x in j['rest']]
    return family
    
class FamilyLoader(object):
    def __init__(self, fname):
        self.f = open(fname, "r")
        size = self.f.read(4)
        self.n = struct.unpack_from("=I", size, 0)[0]
        self.positions = self.f.read(4*(self.n+1))
    def __len__(self): return self.n
    def __getitem__(self, i):
        if not(0 <= i and i < self.n):
            raise IndexError
        offset = struct.unpack_from("=I", self.positions, 4*i)[0]
        next_offset = struct.unpack_from("=I", self.positions, 4*i+4)[0]
        self.f.seek(offset)
        return json.loads(self.f.read(next_offset-offset), object_hook=_decoder)

def _main():
    import pickle
    families = pickle.load(open("libs.families.pickle"))
    save_families(families, "libs.families")
def main():
    import sys
    loader = FamilyLoader("targets/libs.families")
    for a in sys.argv[1:]:
        print str(loader[int(a)]).replace(";","\n").replace("{","\n").replace("}","\n")

if __name__ == "__main__":
    main()
    
def _test():
    loader = FamilyLoader("libs.families")
    print "len is", len(loader)
    c = 0
    for i in loader:
        c += i.head.size()
    print "total size is", c
