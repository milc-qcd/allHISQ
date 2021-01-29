#! /usr/bin/env python

# Python 3 version

import sys, yaml
from TodoUtils import *

# Script for creating todo file entries with precessed source times
# C. DeTar 

######################################################################
def main():

    if len(sys.argv) < 3:
        print("Usage", sys.argv[0], "<series>, <cfglow>, <cfghi>")
        sys.exit(1)

    ( series, cfglow, cfghi ) = sys.argv[1:4]
    if len(series) == 0:
        series = 'a'

    # Parameter file
    YAML = "params-ens.yaml"
    param = loadParam(YAML)
    
    tsrcRange = param['tsrcRange']['loose']
    precessLoose = tsrcRange['precess']
    stepLoose = tsrcRange['step']
    tLooseRange = range(tsrcRange['start'],tsrcRange['stop'],stepLoose)
    print(tLooseRange)

    tsrcRange = param['tsrcRange']['fine']
    precessFine = tsrcRange['precess']
    stepFine = tsrcRange['step']
    tFineRange = range(tsrcRange['start'],tsrcRange['stop'],stepFine)
    print(tFineRange)

    nt = param['ensemble']['dim'][3]
    cfgSep = param['cfgsep'][series]
    cfgnoRange = range(int(cfglow),int(cfghi),int(cfgSep))

    for cfgno in cfgnoRange:
        for tsrc in tLooseRange:
            tShiftLoose = int(cfgno)//cfgSep * precessLoose
            tsrcPrecess = (tsrc + tShiftLoose) % nt
            print("{0:s}.{1:d} L.{2:d}".format(series, cfgno, tsrcPrecess))
        for tsrc in tFineRange:
            tShiftLoose = int(cfgno)//cfgSep * precessLoose
            tShiftFine = int(cfgno)//cfgSep * precessFine * stepLoose
            tsrcPrecess = ( tsrc + tShiftLoose + tShiftFine ) % nt
            print("{0:s}.{1:d} F.{2:d}".format(series, cfgno, tsrcPrecess))

######################################################################
main()
