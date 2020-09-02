# Modules for building keys for sources, propagators, and quarks
# for the Bpilnu project
# C DeTar 5 April 2018

######################################################################
def makeMomKey(mom):
    """Create momentum key"""
    return "{0:d},{1:d},{2:d}".format(*tuple(mom))

######################################################################
def splitMomKey(momKey):
    """Split momentum key"""
    mstr = momKey.split(",")
    mom = list()
    for m in mstr:
        mom.append(int(m))
    return mom

######################################################################
def makeSrcKey(srcAttrs):
    """Create source key"""
    return '.'.join(srcAttrs)

######################################################################
def splitSrcKey(srcKey):
    """Split source key"""
    return srcKey.split(".")

######################################################################
def makeSnkKey(snkAttrs):
    """Create sink key"""
    return ','.join(snkAttrs)

######################################################################
def splitSnkKey(snkKey):
    """Split source key"""
    return snkKey.split(",")

######################################################################
def makeQuarkKey(attrs):
    """Create quark key"""
    return '+'.join(attrs)

######################################################################
def splitQuarkKey(qkKey):
    """Create quark key"""
    return qkKey.split("+")

######################################################################
def cmpQuarkKeys(qkKey1, qkKey2):
    """Compare quark keys"""
    # We must put the point source first 
    (rq1, qk1, m1, e1, r1, srcKey1, snk1) = splitQuarkKey(qkKey1)
    (rq2, qk2, m2, e2, r2, srcKey2, skn2) = splitQuarkKey(qkKey2)
    (src1, mom1) = splitSrcKey(srcKey1)
    (src2, mom2) = splitSrcKey(srcKey2)
    if src1 == 'd':
        order = -1
        if src2 == 'd':
            order = (qkKey1 > qkKey2) - (qkKey2 < qkKey1) 
    elif src2 == 'd':
        order = +1
    else:
        order = (qkKey1 > qkKey2) - (qkKey2 < qkKey1) 

    return order

######################################################################
def cmpQuarkKeys2(qkKey1, qkKey2):
    """Compare quark keys.  This order is for multimass KS"""

    (rq1, qk1, m1, e1, r1, srcKey1, snk1) = splitQuarkKey(qkKey1)
    (rq2, qk2, m2, e2, r2, srcKey2, skn2) = splitQuarkKey(qkKey2)
    (src1, mom1) = splitSrcKey(srcKey1)
    (src2, mom2) = splitSrcKey(srcKey2)

    # Sort first on source and momentum, then on mass
    order = (srcKey1 > srcKey2) - (srcKey1 < srcKey2)
    if order == 0:
        order = (float(m1) > float(m2)) - (float(m1) < float(m2))

    return order

######################################################################
def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

######################################################################
def appendUnique(keys, key):
    """Append to list only if not already in list"""
    if key != None and key not in keys:
        keys.append(key)

