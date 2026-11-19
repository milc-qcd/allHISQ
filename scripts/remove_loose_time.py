#! /usr/bin/env python

import re
import subprocess
import sys, os

# Start with the unpacked files in the fixInDir
# Read correlator files and remove entries belonging to the wrong loose time
# Leave the resulting files in the fixOutDir

# Requires a fiducial tarlist file with one line for each correlator file
# but with "CFG" in place of the configuration number.

######################################################################
def getJobID(tarFile):
    """Extract the jobID from the tarball file name"""

    # Format is Job288265_a000222.tar.bz2

    return re.sub(r'.*Job(\d*)_.*',r'\1' , tarFile)

######################################################################
def getCfg(tarFile):
    """Extract the jobID from the tarball file name"""

    # Format is Job288265_a000222.tar.bz2

    return re.sub(r'.*_(.*)\.tar\.bz2',r'\1', tarFile).rstrip()

######################################################################
def cleanDir(fixInDir):
    """Removes logs and data subdirectories"""

    for d in [ "logs", "data" ]:
        dataPath = os.path.join(fixInDir, d)

        if not os.path.isdir(dataPath):
            continue

        cmd = ' '.join(["rm -r", dataPath ])
        print(cmd)
        
        try:
            subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print("ERROR: rm -r", d, "exited with error code ", e.returncode, ".")
            return 1
    return 0

######################################################################
def unpackTar(fixInDir, tarFilePath):
    """Unpack the tar file into the directory 'fixDir' """

    cmd = ' '.join(["tar -C", fixInDir, "-xjf", tarFilePath ])
    print(cmd)
    
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: unpack tar command exited with code", e.returncode, ".")
        return 1
    return 0

######################################################################
def packTar(fixOutDir, tarFilePath, tarList):
    """Pack the tar file into the directory 'fixDir' """

    cmd = ' '.join(["tar -C", fixOutDir, '--remove-files',
                    "-cjf", tarFilePath, "data logs"])
    print(cmd)

    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: pack tar command exited with code", e.returncode, ".")
        return 1
    return 0

######################################################################
def removeTimeCorr(corrInPath, corrOutPath, deleteTime):
    """Keep only output with the specified jobID"""

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
        # We are dealing with incomplete tar files, so we skip missing files
        return 0

    # Make sure the output directory exists
    (outPath, outFile) = os.path.split(corrOutPath)
    if not os.path.isdir(outPath):
        print("Making dir", outPath)
        os.makedirs(outPath)

    try:
        print("Opening", corrOutPath)
        cfpOut = open(corrOutPath,'w')
    except:
        print("ERROR opening", corrOutPath)
        return 1
    
    # Read correlator stanzas, one at a time.  Write the stanzas we want to keep
    inCorr = False
    linesOut = ""
    t0 = ""
    for line in cfpIn:
        a = line.split()
        if a[0] == '---':
            if inCorr:
                # Flush previous stanza unless we are removing it
                if len(linesOut) > 0 and t0 != deleteTime:
                    cfpOut.write(linesOut)
                linesOut = ""
            inCorr = False
        elif a[0] == "correlator:":
            inCorr = True
        elif a[0] == "JobID:":
            inCorr = False
        elif a[0] == "antiquark_source_origin:":
            # Format is
            # antiquark_source_origin:      [ 0, 0, 0, 78 ]
            t0 = a[5]
        linesOut = linesOut + line

    # Flush previous stanza unless we are removing it
    if len(linesOut) > 0 and t0 != deleteTime:
        cfpOut.write(linesOut)

    cfpOut.close()

    return 0


######################################################################
def removeTimeCorrs(fixInDir, fixOutDir, tarList, cfg, deleteTime):
    """For correlators in the tarList, keep only output with the specified jobID"""
    
    try:
        tfp = open(tarList)
    except:
        print("ERROR opening", tarlist)
        return 1

    for corrFile in tfp:
        corrFile = corrFile.rstrip()
        corrFile = re.sub('CFG', cfg, corrFile)
        corrInPath = os.path.join(fixInDir, corrFile)
        corrOutPath = os.path.join(fixOutDir, corrFile)
        if removeTimeCorr(corrInPath, corrOutPath, deleteTime):
            return 1
    return 0

######################################################################
def copyLogs(fixInDir, fixOutDir):
    """For now we just copy over the log files"""

    inPath = os.path.join(fixInDir, "logs")
    cmd = ' '.join(["cp -r", inPath, fixOutDir])
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: copy logs command exited with code", e.returncode, ".")
        return 1
    return 0

######################################################################
def main():

    if len(sys.argv) < 5:
        print("Usage")
        print(sys.argv[0], "<tarFile> <deleteTime> <fixInDir> <fixOutDir> <tarList>")
        sys.exit(1)

    tarFile = sys.argv[1]
    deleteTime = sys.argv[2]
    fixInDir = sys.argv[3]
    fixOutDir = sys.argv[4]
    tarList = sys.argv[5]
    jobID = getJobID(tarFile)
    cfg = getCfg(tarFile)

    if cleanDir(fixInDir):
        print("Quitting")
        sys.exit(1)

#    tarFilePath = os.path.join(os.getcwd(), fixInDir, tarFile)
#    if unpackTar(fixInDir, tarFilePath ):
#        print("Quitting")
#        sys.exit(1)
        
    if removeTimeCorrs(fixInDir, fixOutDir, tarList, cfg, deleteTime):
        print("Quitting")
        sys.exit(1)

    if copyLogs(fixInDir, fixOutDir):
        print("Quitting")
        sys.exit(1)

#    tarFilePath = os.path.join(os.getcwd(), fixOutDir, tarFile)
#    if packTar(fixOutDir, tarFilePath, tarList):
#        print("Quitting")
#        sys.exit(1)

######################################################################
main()
