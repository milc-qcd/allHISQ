#! /usr/bin/env python

stepLoose = 4
trange = range(0,48,stepLoose)
trangeFine = range(144,144,144)
nt = 144
cfgList = [ 1704 ]
njobs = len(cfgList)
cfgSep = 6
precessLoose = 2
precessFine = 3

print(cfgList)
tShiftLoose = [ 0 ] * njobs

for kjob in range(njobs):
    cfg = cfgList[kjob]
    tShiftLoose[kjob] = int(cfg)//cfgSep * precessLoose

for tsrcBase in trange:
    tsrcs = [ tsrcBase ] * njobs
    for kjob in range(njobs):
        # Add precession shift mod nt
        tsrcs[kjob] = (tsrcBase + tShiftLoose[kjob]) % nt

    print("Loose calculation with tsrcs", tsrcs)

tShiftFine = [ 0 ] * njobs
for kjob in range(njobs):
    cfg = cfgList[kjob]
    tShiftFine[kjob] = int(cfg)//cfgSep * precessFine * stepLoose

for tsrcBase in trangeFine:
    tsrcs = [ tsrcBase ] * njobs
    for kjob in range(njobs):
        # Add precession shift mod nt
        tsrcs[kjob] = ( tsrcBase + tShiftLoose[kjob] + tShiftFine[kjob] ) % nt

    print("Fine calculation with tsrcs", tsrcs)


