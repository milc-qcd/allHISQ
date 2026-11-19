#! /usr/bin/env python

import sys, os, yaml, re, subprocess

verbose = False

# Check an incomplete job to see what loose times have been completed
# C. DeTar 4/5/20

# A job unit consists of a complete run of all steps on a single source time

# Run this script from the ensemble directory

# Usage

#   ../scripts/scan_failed_data.py <run> <seriesCfg> <jobID> <tarList>

#    run           the stream label for the failed run, as in run1b
#    seriesConfig  the series and configuration in the format a.500
#    jobno         the batch job number 
#    tarList       a file with a fiducial list of correlator data files

#    The specific configuration label is replaced by "CFG" as in
#    data/loose/HsV2Hs/m0.022-m0.858-m0.286-p222/corr3pt_T22_CFG

#    The script looks for files in the in the directory tree "run"/data...

verbose = False

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
def scanData(run, precisionLabel, seriesCfg, tarFiles):
    """Scan for completed loose correlator data"""

    tRemove = set()
    tFinished = set()

    try:
        tfp = open(tarFiles)
    except:
        print("ERROR opening", tarlist)
        return tFinished, tRemove1

    series, cfg = decodeSeriesCfg(seriesCfg)
    s06Cfg = codeCfg(series, cfg)

    nDataFinish = None
    for line in tfp:
        corrFile, linesPerTime = line.split()
        corrFile = re.sub('CFG', s06Cfg, corrFile)
        # Look only at the data files with the target precision label
        corrFilePath = os.path.join(run, "data", precisionLabel, corrFile)

        try:
            stat = os.stat(corrFilePath)
        except OSError:
            print("ERROR: can't find required file", corrFilePath)
            tFinished = set()
            return tFinished, tRemove

        # Get stanza count from the number of lines in the file
        cmd = ' '.join(["wc -l", corrFilePath, "| awk '{print $1}'"])
        try:
            haveLines = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            # If we can't find the file, no chance of recovery
            print("ERROR: can't count lines in", corrFile, "return code", e.returncode, ".")
            tFinished = set()
            return tFinished, tRemove

        # Get list of source times in the correlator file
        haveLines = haveLines.rstrip().decode()
        n = int(haveLines)//int(linesPerTime)

        cmd = ' '.join(['grep "antiquark_source_origin:"', corrFilePath, 
                        "| awk '{print $6}'"])
        try:
            tFound = subprocess.check_output(cmd, shell=True).splitlines()
        except subprocess.CalledProcessError as e:
            # If we can't find the file, no chance of recovery
            print("ERROR: can't find source times in", corrFile, "return code", e.returncode, ".")
            tFinished = set()
            return tFinished, tRemove
        # Decode byte encoding
        tFound = set([c.decode() for c in tFound])

        if verbose:
            print("For", corrFilePath, "found", haveLines, "lines with", linesPerTime, "values per time")
            print("Found times", tFound)

        # Consistency check
        if n != len(tFound):
            print("ERROR: Found", len(tFound), precisionLabel, "times, but the file", 
                  corrFile,  "has lines for", n, "loose times")
            tFinished = set()
            return tFinished, tRemove

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

    return tFinished, tRemove

######################################################################
def main():

    # Set permissions
    os.system("umask 022")
    
    # Command-line args:
    if len(sys.argv) < 3:
        print("Usage", sys.argv[0], "<run> <seriesCfg> <tarFiles>")
        sys.exit(1)
        
    (run, seriesCfg, tarFiles) = sys.argv[1:5]

    print("")
    print("")
    print("Scanning in run",run,"for files for",seriesCfg)

    # Load job parameters
    YAMLEns = "params-ens.yaml"
    try:
        param = yaml.safe_load(open(YAMLEns,'r'))
    except:
        print("ERROR: Error loading the parameter files", YAMLEns)
        sys.exit(1)

    # Scan for completed correlator data
    tFinished, tRemove = scanData(run, "loose", seriesCfg, tarFiles)

    # Calculate the recommended loose source time range, based on
    # values in params-ens,yaml
    range = param['tsrcRange']['loose']
    stop = range['stop']
    step = range['step']
    start = range['start'] + step*len(tFinished)

    if len(tFinished) > 0:
        print("The following", len(tFinished), "loose times are common to all correlators:")
        print(sorted(tFinished))
        
        if len(tRemove) > 0:
            print("The following loose times are incomplete and should be removed")
            print(sorted(tRemove))
        else:
            print("No loose times need to be removed")
            print("Recommended loose source range for rerun is", 
                  str(start) + ":" + str(stop) + ":" + str(step))
    else:
        print("No finished sets were found.  Recommend rerunning the entire job")

    # Scan for completed correlator data
    tFinished, tRemove = scanData(run, "fine", seriesCfg, tarFiles)

    # Calculate the recommended loose source time range, based on
    # values in params-ens,yaml
    range = param['tsrcRange']['fine']
    stop = range['stop']
    step = range['step']
    start = range['start'] + step*len(tFinished)

    if len(tFinished) > 0:
        print("The following", len(tFinished), "fine times are common to all correlators:")
        print(sorted(tFinished))
        
        if len(tRemove) > 0:
            print("The following fine times are incomplete and should be removed")
            print(sorted(tRemove))
        else:
            print("No fine times need to be removed")
            print("Recommended fine source range for rerun is", 
                  str(start) + ":" + str(stop) + ":" + str(step))
    else:
        print("No fine sets were found.")

    ######################################################################
main()
