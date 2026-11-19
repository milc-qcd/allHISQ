#! /usr/bin/python3

import re
import subprocess
import sys, os

# Start with the tarball in the fixInDir
# Unpack the tar file into the fixInDir
# Read correlator files and remove entries belonging to the wrong jobID
# Pack the resulting files into a new tarball in the fixOutDir

# Requires a fiducial tarlist file with data entries

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
def cleanCorr(corrInPath, corrOutPath, jobID):
    """Keep only output with the specified jobID"""

    # The file has stanzas beginning with 
    # ---
    # JobID:                        287307

    try:
        cfpIn = open(corrInPath,'r')
    except:
        print("ERROR opening", corrInPath)
        return 1

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
    
    dashes = False
    inJob = False
    inCorr = False
    for line in cfpIn:
        if line.rstrip() == '---':
            dashes = True
            inCorr = False
            continue
        if dashes:
            dashes = False
            a = line.split()
            if a[0] == "JobID:" and a[1] == jobID:
                print('---',file=cfpOut)
                inJob = True
            elif inJob and a[0] == "correlator:":
                print('---',file=cfpOut)
                inCorr = True
                inJob = False
        if inJob or inCorr:
            print(line.rstrip(),file=cfpOut)

######################################################################
def cleanCorrs(fixInDir, fixOutDir, tarList, cfg, jobID):
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
        if cleanCorr(corrInPath, corrOutPath, jobID):
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

    if len(sys.argv) < 4:
        print("Usage")
        print(sys.argv[0], "<tarFile> <fixInDir> <fixOutDir> <tarList>")
        sys.exit(1)

    tarFile = sys.argv[1]
    fixInDir = sys.argv[2]
    fixOutDir = sys.argv[3]
    tarList = sys.argv[4]
    jobID = getJobID(tarFile)
    cfg = getCfg(tarFile)

    if cleanDir(fixInDir):
        print("Quitting")
        sys.exit(1)

    tarFilePath = os.path.join(os.getcwd(), fixInDir, tarFile)
    if unpackTar(fixInDir, tarFilePath ):
        print("Quitting")
        sys.exit(1)
    
    if cleanCorrs(fixInDir, fixOutDir, tarList, cfg, jobID):
        print("Quitting")
        sys.exit(1)

    if copyLogs(fixInDir, fixOutDir):
        print("Quitting")
        sys.exit(1)

    tarFilePath = os.path.join(os.getcwd(), fixOutDir, tarFile)
    if packTar(fixOutDir, tarFilePath, tarList):
        print("Quitting")
        sys.exit(1)

######################################################################
main()
