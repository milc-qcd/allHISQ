#! /usr/bin/env python

import sys, os, yaml, re, subprocess
from allHISQKeys import *
from allHISQFilesNoHiddenSSD import *

verbose = False

# Clean an incomplete job and set up a recovery run.
# C. DeTar 3/23/2020

# A job unit consists of a complete run of all steps on a single source time

# This script starts from the tar files for the incomplete run, or from
# the original "logs" and "data" files and untars them into the "logs" and "data" trees 
# in a working directory

# It then scans the logs in the working directory, checking for what was completed.
# It removes data for unfinished loose source times and for job IDs that do
# not match the specified job ID

# It prints the range of loose source times that still need to be run to complete
# the dataset

# It is assumed that the unfinished results are found in a file tree under
# the directory for the "run" stream, or they are tarred up with tarball
# in either "run" or "run/fail".

# The cleaned logs and data are put in the "run.fix" tree.

# Run this script from the ensemble directory

# Requires...

#  The allHISQ environment used for the original job
#  The subdirectories "run", "run/fail", and "run.fix"
#  A fiducial "tar list" of correlator files with appropriate paths
#  for this run and with line counts for a single source time in
#  that correlator file.  Each line in the file has the format
#  corrfilepath lines-per-source-time

# Usage

#   ../scripts/salvage_job.py <run> <seriesCfg> <jobID> <tarList>

#    run           the stream label for the failed run, as in run1b
#    seriesConfig  the series and configuration in the format a.500
#    jobno         the batch job number 
#    tarList       a file with a fiducial list of correlator data files

#    The paths in tarList are relative to the "run" directory.
#    The specific configuration label is replaced by "CFG" as in
#    data/loose/HsV2Hs/m0.022-m0.858-m0.286-p222/corr3pt_T22_CFG

#######################################################################
def decodeSeriesCfg(seriesCfg):
    """Decode series, cfg, as it appeaers in the todo file"""
    return seriesCfg.split(".")

############################################################
def loadParamsJoin(YAMLEns, YAMLAll):
    """Concatenate two YAML parameter files and load
    We need this because YAMLEns defines a reference needed
    by YAMLAll"""
    
    # Initial parameter file
    try:
        ens = open(YAMLEns,'r').readlines()
        all = open(YAMLAll,'r').readlines()
        param = yaml.safe_load("".join(ens+all))
    except:
        print("ERROR: Error loading the parameter files", YAMLEns, YAMLAll)
        sys.exit(1)

    return param

############################################################
def loadParam(YAML):
    """Load a YAML parameter file"""

    # Initial parameter file
    try:
        param = yaml.safe_load(open(YAML,'r'))
    except:
        print("ERROR: Error loading the parameter file", YAML)
        sys.exit(1)

    return param

############################################################
def updateParam(param, paramUpdate):
    """Update the param dictionary according to terms in paramUpdate"""

    # Updating is recursive in the tree so we can update selected branches
    # leaving the remainder untouched
    for b in paramUpdate.keys():
        try:
            k = paramUpdate[b].keys()
            n = len(k)
        except AttributeError:
            n = 0

        if b in param.keys() and n > 0:
            # Keep descending until we run out of branches
            updateParam(param[b], paramUpdate[b])
        else:
            # Then stop, replacing just the last branch or creating a new one
            param[b] = paramUpdate[b]

    return param

############################################################
def loadParams(YAMLAll, YAMLEns, YAMLMachine):
    """Load a set of YAML parameter files into a single dictionary"""

    # Initial parameter file
    param = loadParamsJoin(YAMLEns, YAMLAll)
        
    # Load parameters specific to the machine and installation
    paramMachine = loadParam(YAMLMachine)
    param = updateParam(param, paramMachine)

    # Add the remote and archive roots to the yaml-generated dictionary:
    addRootPaths(param)

    return param

######################################################################
def setUpReadJobTarFile(param, configId, jobID, subDirs):
    """Define and open the tar file"""

    root = param['files']['root']
    localRoot = root['local']

    ensemble = param['ensemble']
    tag = ''

    io = param['files']['tar']
    name = tarFileName(configId, jobID, tag)
    localpath = os.path.join( root[io['root']] )
    tar = StageFile(localRoot, subDirs, localpath, subDirs, 
                    name, 'r', None, False)

    return tar
    
######################################################################
def setUpWriteJobTarFile(param, configId, jobID):
    """Define and open the tar file"""

    root = param['files']['root']
    localRoot = root['local']

    ensemble = param['ensemble']
    stream = param['stream']
    tag = ''

    io = param['files']['tar']
    name = tarFileName(configId, jobID, tag)
    localpath = os.path.join( root[io['root']] )
    subDirs = [stream]
    tar = StageFile(localRoot, subDirs, localpath, subDirs, 
                    name, 'w', None, False)

    return tar
    
############################################################
def tarList(tarbase, dirs, suffix, cfg):
    """Construct a list of files for including in the tar ball"""
    # Lists all files in the dirs ending with the specified suffix and cfg number
    
    configId = codeCfg(suffix, cfg)
    # Name of the tar-list file
    tList = "tar." + configId
    tListPath = tarbase + "/" + tList
    # First delete any stale tar-list file
    cmd = ['/bin/rm -f', tListPath]
    cmd = ' '.join(cmd)
    try:
        lines = subprocess.check_output(cmd, shell = True).splitlines()
    except subprocess.CalledProcessError as e:
        print("Error deleting", tList)
    for d in dirs:
        cmd0 = ['cd', tarbase]
        cmd0 = ' '.join(cmd0)
        cmd1 = ['/bin/find', d, '-name', "'*" + configId + "'", '-print', ">>", tList]
        cmd1 = ' '.join(cmd1)
        cmd = ";".join([cmd0, cmd1]);
        print("#", cmd)
        try:
            lines = subprocess.check_output(cmd, shell = True).splitlines()
        except subprocess.CalledProcessError as e:
            print("Error finding files in", tarbase, d)
    return tListPath
    
############################################################
def storeTarFile(param, seriesCfg, tar):
    """Create and copy tar file to the archive and clean up"""

    suffix, cfg = decodeSeriesCfg(seriesCfg)

    # Create tarball and store it
    tarbase = tar.dirLocal()
    if tarbase == None:
        tarbase = tar.dirRemote()
    tardirs = param['files']['tar']['list']

    # Get a list of paths in the directories tardirs with matching configuration number
    tListPath = tarList( tarbase, tardirs, suffix, cfg )

    # Make sure we don't clobber an existing tar file
    if os.access(tar.path(), os.R_OK):
        msg = " ".join(["ERROR:", tar.path(), "already exists.  Not clobbering it.","\n"])
        sys.stderr.write(msg)
        sys.exit(1)
    else:
        # Create the tarball and check it for completeness
        cmd = ['/bin/tar', '-C', tarbase, '--remove-files', '-cjf', tar.path(), '-T', tListPath]
        cmd = ' '.join(cmd)
        print("#", cmd)
        subprocess.check_output(cmd, shell = True)

        tar.store()

######################################################################
def defineTarFile(param, seriesCfg, jobID):
    """Define the tar file for this cfg and step"""

    configId = decodeSeriesCfg(seriesCfg)

    tar = setUpWriteJobTarFile(param, configId, jobID)

    return tar
    
######################################################################
def findJobTarFile(param, run, seriesCfg, jobID):
    """Find the tar file for the failed job or create it"""

    configId = decodeSeriesCfg(seriesCfg)

    # Look first in the run/fail directory
    tarFile = setUpReadJobTarFile(param, configId, jobID, [run, "fail"])
    if tarFile.exist():
        return tarFile

    # Next look in the run directory
    tarFile = setUpReadJobTarFile(param, configId, jobID, [run])
    if tarFile.exist():
        return tarFile

    # Try creating the tar file from run/data and run/logs
    tarFile = setUpWriteJobTarFile(param, configId, jobID)

    print("Creating tar file", tarFile.path())
    storeTarFile(param, seriesCfg, tarFile)
#    tarFile.close()

    # Try again in the run directory
    tarFile = setUpReadJobTarFile(param, configId, jobID, [run])
    if tarFile.exist():
        return tarFile
    else:
        print("Couldn't find or create the tar file for", configId, "job", jobID)
        return None

######################################################################
def unpackTar(fixInDir, tarFilePath):
    """Unpack the tar file into the directory 'fixInDir' """

    cmd = ' '.join(["tar -C", fixInDir, "-xjf", tarFilePath ])
    print(cmd)
    
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: unpack tar command exited with code", e.returncode, ".")
        return 1
    return 0

######################################################################
def setUpWorkDir(fixPathIn, tarFilePath):
    """Unpack the file into a working directory for cleaning up the run"""

    print("Creating a working directory",fixPathIn)
    makePath(fixPathIn)

    # Unpack the tarfile into the working directory
    unpackTar(fixPathIn, tarFilePath)

######################################################################
def extractTime(path):
    """Extract the source time from the output file path"""
    # Format is 
    # run1b.fix/fix_in/logs/loose/outJob683221_step2_t36.a003348

    time = re.sub('.*_t','',path)
    time = re.sub('\..*','',time)

    return time

######################################################################
def scanData(param, run, seriesCfg, jobID, fixPathIn, tarFiles):
    """Scan for completed loose correlator data"""
    try:
        tfp = open(tarFiles)
    except:
        print("ERROR opening", tarlist)
        return 1

    series, cfg = decodeSeriesCfg(seriesCfg)
    s06Cfg = codeCfg(series, cfg)

    nDataFinish = None
    for line in tfp:
        corrFile, linesPerTime = line.split()
        corrFile = re.sub('CFG', s06Cfg, corrFile)
        # Look only at the loose data files
        if not "loose" in corrFile:
            continue
        corrFilePath = os.path.join(fixPathIn, corrFile)

        try:
            stat = os.stat(corrFilePath)
        except OSError:
            print("ERROR: can't find required file", corrFilePath)
            return 0

        cmd = ' '.join(["wc -l", corrFilePath, "| awk '{print $1}'"])
        try:
            haveLines = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            # If we can't find the file, no chance of recovery
            print("ERROR: can't count lines in", corrFile, "return code", e.returncode, ".")
            return 0

        haveLines = haveLines.rstrip()
        if verbose:
            print("For", corrFilePath, "found", haveLines, "lines with", linesPerTime, "values per time")
        n = int(haveLines.decode())//int(linesPerTime)
        if nDataFinish == None:
            nDataFinish = n
        elif n < nDataFinish:
            nDataFinish = n

    return nDataFinish

######################################################################
def scanLogs(param, run, seriesCfg, jobID, fixPathIn):
    """Scan for completed loose source times"""

    suffix, cfg = decodeSeriesCfg(seriesCfg)
    tsrcConfigId = (999, suffix, int(cfg))

    name = outFileName(run, tsrcConfigId, jobID, '', "step2")
    # Replace time 999 with wild card
    name = re.sub('999', '*', name)

    path = buildPath(fixPathIn, ["logs", "loose", name])
    
    cmd = ' '.join(['grep "RUNNING COMPLETED"', path])
    print("#", cmd)
    
    try:
        finished = subprocess.check_output(cmd, shell = True).splitlines()
    except subprocess.CalledProcessError as e:
        print("Error finding a completed set of output files")
        print("Recommend redoing the job from the start")
        sys.exit(1)

    cmd = ' '.join(["ls -1t", path])
    print("#", cmd)

    try:
        attempted = subprocess.check_output(cmd, shell = True).splitlines()
    except subprocess.CalledProcessError as e:
        print("Internal error finding output files")
        sys.exit(1)

    tFinished = []
    for i in range(len(finished)):
        tFinished = tFinished + [extractTime(finished[i].decode())]

    return tFinished

######################################################################
def filterTimeCorr(corrInPath, corrOutPath, jobID, keepTimes):
    """Keep only output with the specified jobID and without the specified times"""

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
        cfpIn = open(corrInPath,'r')
    except:
        print("ERROR opening", corrInPath)
        return 1

    # Make sure the output directory exists
    (outPath, outFile) = os.path.split(corrOutPath)
    if not os.path.isdir(outPath):
        if verbose:
            print("Making dir", outPath)
        os.makedirs(outPath)

    try:
        if verbose:
            print("Opening", corrOutPath)
        cfpOut = open(corrOutPath,'w')
    except:
        print("ERROR opening", corrOutPath)
        return 1
    
    # Read correlator stanzas, one at a time.  Write the stanzas we want to keep
    inCorr = False
    linesOut = ""
    t0 = ""
    haveJobID = ""
    for line in cfpIn:
        a = line.split()
        if a[0] == '---':
            if inCorr:
                # Flush previous stanza unless we are removing it
                if len(linesOut) > 0 and t0 in keepTimes and haveJobID == jobID:
                    cfpOut.write(linesOut)
                linesOut = ""
            inCorr = False
        elif a[0] == "correlator:":
            inCorr = True
        elif a[0] == "JobID:":
            haveJobID = a[1]
            inCorr = False
        elif a[0] == "antiquark_source_origin:":
            # Format is
            # antiquark_source_origin:      [ 0, 0, 0, 78 ]
            t0 = a[5]
        linesOut = linesOut + line

    # Flush previous stanza unless we are removing it
    if len(linesOut) > 0 and t0 in keepTimes and haveJobID == jobID:
        cfpOut.write(linesOut)

    cfpOut.close()
    cfpIn.close()

    return 0


######################################################################
def filterTimeCorrs(fixInDir, fixOutDir, tarFiles, cfg, jobID, keepTimes):
    """For correlators in the tarFiles, keep only output with the specified jobID"""
    
    try:
        tfp = open(tarFiles)
    except:
        print("ERROR opening", tarlist)
        return 1

    for line in tfp:
        corrFile, count = line.split()
        # corrFile = corrFile.rstrip()
        corrFile = re.sub('CFG', cfg, corrFile)
        corrInPath = os.path.join(fixInDir, corrFile)
        corrOutPath = os.path.join(fixOutDir, corrFile)
        if filterTimeCorr(corrInPath, corrOutPath, jobID, keepTimes):
            return 1
    return 0

######################################################################
def removeFineData(fixPathIn):

    finePathIn = os.path.join(fixPathIn, "data", "fine")
    cmd = ' '.join(["/bin/rm -rf", finePathIn ])

    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't remove fine data. Exit code", e.returncode, ".")
        return 1
    return 0

######################################################################
def copyData(fixInDir, fixOutDir):
    """Copy the completed loose source time data"""

    inPath = os.path.join(fixInDir, "data", "loose")
    outPath = os.path.join(fixOutDir, "data")
    cmd = ' '.join(["rsync -acr", inPath, outPath])
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: copy data command exited with code", e.returncode, ".")
        return 1
    return 0

######################################################################
def copyLogs(fixInDir, fixOutDir):
    """For now we just copy over the log files"""

    inPath = os.path.join(fixInDir, "logs")
    cmd = ' '.join(["rsync -acr", inPath, fixOutDir])
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: copy logs command exited with code", e.returncode, ".")
        return 1
    return 0

######################################################################
def cleanCorrs(fixPathIn, fixPathOut, tarFiles, seriesCfg, jobID, tFinished):
    """Clean the correlators"""

    series, cfg = decodeSeriesCfg(seriesCfg)
    s06Cfg = codeCfg(series, cfg)

    # Check to be sure the output directory is clean
#    cmd = ' '.join([ "find", fixPathOut, "-name \'*" + s06Cfg + "\' -print"])
#    print("#", cmd)
#    try:
#        lines = subprocess.check_output(cmd, shell=True).splitlines()
#    except subprocess.CalledProcessError as e:
#        print("ERROR: find files command exited with code", e.returncode, ".")
#    if len(lines) > 0:
#        print("Under", fixPathOut, "there are", len(lines), "files with names ending in", s06Cfg)
#        reply = input("Remove those files before proceeding? (y/n) ")
#        if reply == 'y':
#            cmd = ' '.join([ "find", fixPathOut, "-name \'*" + s06Cfg + "\' -exec /bin/rm \'{}\' \;"])
#            print("#", cmd)
#            try:
#                subprocess.check_output(cmd, shell=True)
#            except subprocess.CalledProcessError as e:
#                print("The command to remove files failed")
#                return 1
#        else:
#            print("Files with the same name will simply be overwritten")

    # Remove data for the unfinished loose source time and stale jobIDs
    if filterTimeCorrs(fixPathIn, fixPathOut, tarFiles, s06Cfg, jobID, tFinished):
        return 1

    # Simply copy the log files
    if copyLogs(fixPathIn, fixPathOut):
        return 1

    return 0

######################################################################
def main():

    # Set permissions
    os.system("umask 022")
    
    # Command-line args:
    if len(sys.argv) < 4:
        print("Usage", sys.argv[0], "<run> <seriesCfg> <jobID> <tarFiles>")
        sys.exit(1)
        
    (run, seriesCfg, jobID, tarFiles) = sys.argv[1:5]

    # Load job parameters
    YAML = "../scripts/params-allHISQ-plus4.yaml"
    YAMLEns = "params-ens.yaml"
    YAMLMachine = "params-machine.yaml"
    
    # Load the basic parameter set
    param = loadParams(YAML, YAMLEns, YAMLMachine)
    
    # Working directory for fixing the files
    fixPathIn = run+".fix/fix_in"
    fixPathOut = run+".fix"

    # Find the tar file for this run
    # First look where we put tar files for failed runs
    tarFile = findJobTarFile(param, run, seriesCfg, jobID)
    
    if tarFile == None:
        print("Quitting")
        sys.exit(1)
    else:
        print("Working with tarfile", tarFile.path())

    # Unpack the tarfile into a working directory for cleaning up the run
    setUpWorkDir(fixPathIn, tarFile.path())

    # Scan for completed correlator data
    nDataFinish = scanData(param, run, seriesCfg, jobID, fixPathIn, tarFiles)

    # Scan logs for completed loose source times
    tFinished = scanLogs(param, run, seriesCfg, jobID, fixPathIn)
    nLogFinish = len(tFinished)
    print("There are", nLogFinish, "completed loose log file sets with times:")
    print(tFinished)

    if nLogFinish == 0:
        print("No complete loose source times found. Recommend rerunning the entire job")
        sys.exit(1)

    if nLogFinish > nDataFinish:
        print("Some correlator file(s) had only", nDataFinish, "loose-time stanzas")
        print("Apparently, data are unexpectedly missing. Recommend rerunning the entire job")
        sys.exit(1)
    
    print("Copying data only for job ID", jobID, "and with the above loose source times.")
    if cleanCorrs(fixPathIn, fixPathOut, tarFiles, seriesCfg, jobID, tFinished):
        print("Quitting")
        sys.exit(1)

    # Calculate the recommended loose source time range, based on
    # values in params-ens,yaml
    range = param['tsrcRange']['loose']
    stop = range['stop']
    step = range['step']
    start = range['start'] + step*nLogFinish

    print("Recommended loose source range for rerun is", 
          str(start) + ":" + str(stop) + ":" + str(step))

######################################################################
main()
