#! /usr/bin/env python

trange = range(48,52,4)
njobs = 1
nt = 144
cfgList = [ 756 ]
cfgSep = 6
precess = 2
tShift = [ 0 ] * njobs

for tsrcBase in trange:
    tsrcs = [ tsrcBase ] * njobs
    for kjob in range(njobs):
        # Compute the precession shift for the source times, 
        # based on the cfg number in this group
        cfg = cfgList[kjob]
        tShift[kjob] = int(cfg)//cfgSep*precess
                    
        # Add precession shift mod nt
        tsrcs[kjob] = (tsrcBase + tShift[kjob]) % nt

    print("Loose calculation with tsrcs", tsrcs)

