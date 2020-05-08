#! /usr/bin/python3

import re
import subprocess
import sys, os

verbose = False

# Start with the "data" and "logs" unpacked and in the "run" directory tree
# Scan data to find what has been completed
# Rewrite the correlator data keeping only one copy of each completed time

# Usage

#  clean_corrs.py <run> <seriesCfg> <tarList>")

#  run        The run directory name containing "data" and "logs"
#  seriesCfg  The configuraition label, as in a.505
#  tarList    The complete list of paths to the correlator data, starting from the "loose"
#             or "fine" subdirectories

# Format of tarList: one line for each correlator file
# but with "CFG" in place of the configuration number and a line count for
# data for a single time slice.  These values are used in conjunction with
# the antiquark_source_origin to determine completeness

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
def filterTimeCorr(corrPath, keepTimes, linesPerTime):
    """Keep only one copy of output with the specified list of times"""

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
        return 1

    remainingTimes = set(keepTimes)
    
    # Read correlator stanzas, one at a time.  Write the stanzas we want to keep
    inCorr = False
    linesStanza = ""
    linesCorrFile = ""
    t0 = ""
    linect = 0
    for line in cfp:
        a = line.split()
        if a[0] == '---':
            if inCorr:
                # Flush previous stanza unless we are removing it
                if len(linesStanza) > 0 and t0 in remainingTimes:
                    linesCorrFile += linesStanza
                linesStanza = ""
            inCorr = False
        elif a[0] == "correlator:":
            inCorr = True
        elif a[0] == "JobID:":
            inCorr = False
            remainingTimes.discard(t0)
            linesStanza = '---\n'
            linect = 1
        elif a[0] == "antiquark_source_origin:":
            # Format is
            # antiquark_source_origin:      [ 0, 0, 0, 78 ]
            t0 = a[5]
        # Drop excess lines in stanza
        if linect < linesPerTime:
            linesStanza += line
        linect += 1

    # Flush previous stanza unless we are removing it
    if inCorr and len(linesStanza) > 0 and t0 in remainingTimes:
        linesCorrFile += linesStanza
        remainingTimes.discard(t0)
        
    if len(remainingTimes) > 0:
        print("ERROR: the following times were unexpectedly missing from", corrPath)
        print(remainingTimes)
        return 1
    
    cfp.close()

    try:
        cfp = open(corrPath,'w')
    except:
        print("ERROR opening", corrPath,"for writing")
        
    cfp.write(linesCorrFile)
    cfp.close()

    return 0

######################################################################
def filterTimeCorrs(run, precisionLabel, tarList, s06Cfg, keepTimes):
    """For correlators in the tarFiles, keep only output with the specified jobID"""
    
    try:
        tfp = open(tarList)
    except:
        print("ERROR opening", tarList)
        return 1

    for line in tfp:
        corrFile, linesPerTime = line.split()
        linesPerTime = int(linesPerTime)
        corrFile = re.sub('CFG', s06Cfg, corrFile)
        corrPath = os.path.join(run, "data", precisionLabel, corrFile)
        if filterTimeCorr(corrPath, keepTimes, linesPerTime):
            return 1
    return 0

######################################################################
def scanData(run, precisionLabel, s06Cfg, tarList):
    """Scan for completed loose correlator data"""
    try:
        tfp = open(tarList)
    except:
        print("ERROR opening", tarList)
        sys.exit(1)

    tRemove = set()
    tFinished = set()
    tSurplusData = set()
    nDataFinish = None
    nExtra = 0
    nBadMeasure = 0
    nMissing = 0
    first = True
    for line in tfp:
        corrFile, linesPerTime = line.split()
        corrFile = re.sub('CFG', s06Cfg, corrFile)
        corrFilePath = os.path.join(run, "data", precisionLabel, corrFile)
        linesPerTime = int(linesPerTime)

        try:
            stat = os.stat(corrFilePath)
        except OSError:
            if not first:
                print("ERROR: can't find required file", corrFilePath)
            nMissing += 1
            continue
        first = False

        # Get stanza count from the number of lines in the file
        cmd = ' '.join(["wc -l", corrFilePath, "| awk '{print $1}'"])
        try:
            haveLines = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            # If we can't find the file, no chance of recovery
            print("ERROR: can't count lines in", corrFile, "return code", e.returncode, ".")
            return tFinished, tRemove, nExtra, nBadMeasure, nMissing

        # Check line count
        haveLines = int(haveLines.rstrip().decode())
        if haveLines % linesPerTime != 0:
            nBadMeasure += 1
            
        n = haveLines//int(linesPerTime)

        # Get list of source times in the correlator file
        cmd = ' '.join(['grep "antiquark_source_origin:"', corrFilePath, 
                        "| awk '{print $6}'"])
        try:
            tFoundList = subprocess.check_output(cmd, shell=True).splitlines()
        except subprocess.CalledProcessError as e:
            # If we can't find the file, no chance of recovery
            print("ERROR: can't find source times in", corrFile, "return code", e.returncode, ".")
            return tFinished, tRemove, nExtra, nBadMeasure, nMissing
        # Decode byte encoding
        tFound = set([c.decode() for c in tFoundList])

        if verbose:
            print("For", corrFilePath, "found", haveLines, "lines with", 
                  linesPerTime, "values per time")
            print("Found times", tFound)

        # Consistency check
        if n > len(tFound):
            nExtra += 1
        elif n < len(tFound):
            print("FATAL:", corrFilePath, "lists more time values than its length permits")
            sys.exit(1)

        # tFinished will be a list of all times common to all correlators
        if len(tFinished) > 0:
            tFinished = tFinished.intersection(tFound)
        else:
            tFinished = tFound

        # tRemove will be a list of all times not common to all correlators
        tSpare = tFound.difference(tFinished)
        if len(tSpare) > 0:
            tRemove.update(tSpare)

        if nDataFinish == None:
            nDataFinish = n
        elif n < nDataFinish:
            nDataFinish = n

        # Get the locations of the JobID lines
        cmd = ' '.join(["grep -n JobID", corrFilePath, "| awk -F: '{print $1}'"])
        try:
            jobIDLines = subprocess.check_output(cmd, shell=True).splitlines()
        except subprocess.CalledProcessError as e:
            # If we can't find the file, no chance of recovery
            print("ERROR: can't count lines in", corrFilePath, "return code", e.returncode, ".")
            return tFinished, tRemove, nExtra, nBadMeasure, nMissing
        # Decode byte encoding
        jobIDLines = [int(c.decode()) for c in jobIDLines]

        # Check locations of JobID lines
        if len(jobIDLines) == 0:
            print("ERROR: No JobID lines in", corrFilePath)
            tFinished = set()
            return tFinished, tRemove, nExtra, nBadMeasure, nMissing
        if jobIDLines[0] != 2:
            print("ERROR: First JobID line is at line no", jobIDLines[0], 
                  "but should be at line 2 in", corrFilePath)
        # Add an extrapolated location for the last stanza
        jobIDLines += [haveLines + 2]
            
        # Check for correct spacing of jobID lines
        for k in range(1,len(jobIDLines)):
            linect = jobIDLines[k] - jobIDLines[k-1]
            if linect < linesPerTime:
                t0 = int(tFoundList[k-1].decode())
                if t0 in tFinished:
                    print("ERROR: stanza for time", t0, "in", corrFilePath, 
                          "has line count", linect, "but wanted", linesPerTime)
                    print("That time will be dropped")
                    tFinished.discard(t0)
                    tRemove.update([t0])
            elif linect > linesPerTime:
                t0 = int(tFoundList[k-1].decode())
                if t0 not in tSurplusData:
                    print("ERROR: stanza for time", t0, "in", corrFilePath, "has line count", 
                          linect, "but wanted", linesPerTime)
                    print("The extra lines will be dropped")
                    tSurplusData.update([t0])

    if nExtra > 0:
        print("ERROR: in", nExtra, precisionLabel,
              "correlator files there was a mismatch between the time stanza count",
              "and the number of unique source times")
    if nBadMeasure > 0:
        print("ERROR: In", nBadMeasure,  precisionLabel, nBadMeasure,
              "correlator files the line count was not an integer multiple of the fiducial count",
              "per stanza, indicating either extra or missing lines.")

    return tFinished, tRemove, nExtra, nBadMeasure, nMissing

######################################################################
def main():

    if len(sys.argv) < 4:
        print("Usage")
        print(sys.argv[0], "<run> <seriesCfg> <tarList>")
        sys.exit(1)

    ( run, seriesCfg, tarList ) = sys.argv[1:4]

    series, cfg = decodeSeriesCfg(seriesCfg)
    s06Cfg = codeCfg(series, cfg)

    print(sys.argv)

    # Scan loose data set for completed correlator data
    print("Scanning the loose data set")
    tFinished, tRemove, nExtra, nBadMeasure, nMissing  = scanData( run, "loose", s06Cfg, tarList )

    if len(tFinished) == 0:
        print("No finished sets were found.  Recommend rerunning the entire job")
    else:
        print("The following", len(tFinished), "loose times are common to all correlators:")
        print(sorted(tFinished))
        
        if len(tRemove) > 0 or nExtra > 0 or nBadMeasure > 0 or nMissing > 0:
            if len(tRemove) > 0:
                print("The following loose time sets are incomplete and will be removed")
                print(sorted(tRemove))

            if nExtra > 0:
                print("Duplicate loose time stanzas were found and will be removed")

            if nBadMeasure > 0:
                print("Possible surplus data were found and will be removed")

            if nMissing > 0:
                print("There were", nMissing, "missing loose correlstors.  Recommend rerunning the job.")

            # Rewrite all correlator files, keeping only those with tFinished
            if filterTimeCorrs(run, "loose", tarList, s06Cfg, tFinished):
                print("Quitting")
                sys.exit(1)
        else:
            print("No loose times need to be removed")

    # Scan fine data set for completed correlator data
    print("Scanning the fine data set (if it exists)")
    tFinished, tRemove, nExtra, nBadMeasure, nMissing = scanData( run, "fine", s06Cfg, tarList )

    if len(tFinished) == 0:
        print("There were missing completed fine data sets.")

    else:
        print("The following", len(tFinished), "fine times are common to all correlators:")
        print(sorted(tFinished))
        
        if len(tRemove) > 0 or nExtra > 0 or nMissing > 0:
            if len(tRemove) > 0:
                print("The following fine times are incomplete and will be removed")
                print(sorted(tRemove))

            if nExtra > 0:
                print("Duplicate fine time stanzas were found and will be removed")

            if nBadMeasure > 0:
                print("Possible surplus data were found and will be removed")

            if nMissing > 0:
                print("There were", nMissing, "missing fine correlstors.  Recommend rerunning the job.")

            # Rewrite all correlator files, keeping only those with tFinished
            if filterTimeCorrs(run, tarList, s06Cfg, tFinished):
                print("Quitting")
                sys.exit(1)

######################################################################
main()
