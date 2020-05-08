#! /usr/bin/python3

import re
import subprocess
import sys, os

# Start with the unpacked files in the run directory "run"
# Read correlator files and remove entries belonging to the wrong loose time
# Replace the correlator file in the fixDir

# Requires a fiducial tarlist file with one line for each correlator file
# but with "CFG" in place of the configuration number.
# Format ...
# pi/m0.0024-m0.0024-p100/corr2pt_CFG 177
# pi/m0.0024-m0.0024-p222/corr2pt_CFG 177


#######################################################################
def decodeSeriesCfg(seriesCfg):
    """Decode series, cfg, as it appeaers in the todo file"""
    return seriesCfg.split(".")

######################################################################
def codeCfg(suffix, cfg):
    """Encode tsrc and cfg for file names"""
    if suffix == '' or suffix == None:
        config = { 'series': 'a', 'trajectory': int(cfg) }
    else:
        config = { 'series': suffix, 'trajectory': int(cfg) }
    return '%(series)s%(trajectory)06d' % config

######################################################################
def removeTimeCorr(corrPath, deleteTimes):
    """Skip output with the specified deleteTimes"""

    # The file has stanzas beginning with 
    # ---
    # JobID:                        287307
    # Followed by metadata, ending with
    # ...
    # ---
    # correlator:                   P5-P5
    # Followed by further metadata and correlator values
    # Followeid by an EOF or a new stanza

    try:
        cfp = open(corrPath,'r')
    except:
        print("ERROR opening", corrPath, "for reading.")
        # We are dealing with incomplete tar files, so we skip missing files
        return 0

    # Read correlator stanzas, one at a time.  Write the stanzas we want to keep
    inCorr = False
    linesStanza = ""
    linesCorrFile = ""
    t0 = ""
    for line in cfp:
        a = line.split()
        if a[0] == '---':
            if inCorr:
                # Flush previous stanza unless we are removing it
                if len(linesStanza) > 0 and t0 not in deleteTimes:
                    linesCorrFile += linesStanza
                linesStanza = ""
            inCorr = False
        elif a[0] == "correlator:":
            inCorr = True
        elif a[0] == "JobID:":
            inCorr = False
        elif a[0] == "antiquark_source_origin:":
            # Format is
            # antiquark_source_origin:      [ 0, 0, 0, 78 ]
            t0 = a[5]
        linesStanza += line

    # Flush previous stanza unless we are removing it
    if len(linesStanza) > 0 and t0 not in deleteTimes:
        linesCorrFile += linesStanza

    cfp.close()

    try:
        cfp = open(corrPath,'w')
    except:
        print("ERROR opening", corrPath,"for writing")

    cfp.write(linesCorrFile)
    cfp.close()

    return 0


######################################################################
def removeTimeCorrs(run, precisionLabel, tarList, s06Cfg, deleteTimes):
    """For correlators in the tarList, keep output unless it has the
    specified deleteTimes"""
    
    try:
        tfp = open(tarList)
    except:
        print("ERROR opening", tarlist)
        return 1

    for line in tfp:
        corrFile, count = line.split()
        corrFile = re.sub('CFG', s06Cfg, corrFile)
        corrPath = os.path.join(run, "data", precisionLabel, corrFile)
        if removeTimeCorr(corrPath, deleteTimes):
            return 1
    return 0

######################################################################
def main():

    if len(sys.argv) < 6:
        print("Usage")
        print(sys.argv[0], " <run> <loose|fine> <seriesCfg> <deleteTime> <tarList>")
        sys.exit(1)
        
    ( run, precisionLabel, seriesCfg, deleteTime, tarList )  = sys.argv[1:6]

    # Translate cfg-series label as in a.504 -> a000504
    series, cfg = decodeSeriesCfg(seriesCfg)
    s06Cfg = codeCfg(series, cfg)

    if removeTimeCorrs(run, precisionLabel, tarList, s06Cfg, [ deleteTime ]):
      print("Quitting")
      sys.exit(1)

######################################################################
main()
