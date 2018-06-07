# Modules for building keys for sources, propagators, and quarks
# for the Bpilnu project
# C DeTar 5 April 2018

######################################################################
def makeMomKey(mom):
    """Create momentum key"""
    return '%d,%d,%d' % tuple(mom)

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
            order = cmp(qkKey1, qkKey2)
    elif src2 == 'd':
        order = +1
    else:
        order = cmp(qkKey1, qkKey2)

    return order

######################################################################
def cmpQuarkKeys2(qkKey1, qkKey2):
    """Compare quark keys.  This order is for multimass KS"""

    (rq1, qk1, m1, e1, r1, srcKey1, snk1) = splitQuarkKey(qkKey1)
    (rq2, qk2, m2, e2, r2, srcKey2, skn2) = splitQuarkKey(qkKey2)
    (src1, mom1) = splitSrcKey(srcKey1)
    (src2, mom2) = splitSrcKey(srcKey2)

    # Sort first on source and momentum, then on mass
    order = cmp(srcKey1, srcKey2)
    if order == 0:
        order = cmp(float(m1), float(m2))

    return order

######################################################################
def appendUnique(keys, key):
    """Append to list only if not already in list"""
    if key != None and key not in keys:
        keys.append(key)

