#! /usr/bin/env python

# Python 3 version

import sys, os, yaml, re, subprocess, copy
from TodoUtils import *
from allHISQFiles import *
from Cheetah.Template import Template

# Check job completion.  For any completed jobs, mark the todo list
# C. DeTar

# Usage

# From the ensemble directory containing the todo file
# ../../scripts/check_completed.py

# Requires a todo file with a list of configurations to be processed
# In addition to the modules imported above, requires the following YAML files:
# ../scripts/params-allHISQ-plus5.yaml
# ../scripts/params-launch.yaml
# params-machine.yaml
# params-ens.yaml

######################################################################
def jobStillQueued(param,jobID):
    """Get the status of the queued job"""
    # This code is locale dependent

    locale = param['submit']['locale']
    scheduler = param['launch'][locale]['scheduler']
    
    user = os.environ['USER']
    if scheduler == 'LSF':
        cmd = " ".join(["bjobs", "-u", user, "|", "grep -w", jobID])
    elif scheduler == 'PBS':
        cmd = " ".join(["qstat", "-u", user, "|", "grep -w", jobID])
    elif scheduler == 'SLURM':
        cmd = " ".join(["squeue", "-u", user, "|", "grep -w", jobID])
    elif scheduler == 'Cobalt':
        cmd = " ".join(["qstat", "-fu", user, "|", "grep -w", jobID])
    else:
        print("Don't recognize scheduler", scheduler)
        print("Quitting")
        sys.exit(1)
    reply = ""
    try:
        reply = subprocess.check_output(cmd, shell = True)
    except subprocess.CalledProcessError as e:
        status = e.returncode
        # If status is other than 0 or 1, we have a qstat problem
        # Treat job as unfinished
        if status != 1:
            print("Error", status, "Can't get the job status.  Skipping.")
            return True

    if len(reply) > 0:
        a = reply.split()
        if scheduler == 'LSF':
            time = a[5] + " " +  a[6] + " " + a[7]  # Actually the start time
            field = "start"
            jobstat = a[2]
        elif scheduler == 'PBS':
            time = a[8]
            field = "queue"
            jobstat = a[9]
        elif scheduler == 'SLURM':
            time = a[5]
            field = "run"
            jobstat = a[4]
        elif scheduler == 'Cobalt':
            time = a[5]
            field = "run"
            jobstat = a[8]
        else:
            print("Don't recognize scheduler", scheduler)
            print("Quitting")
            sys.exit(1)

        print("Job status", jobstat.decode(), field, "time", time.decode())
        # If job is being canceled, jobstat = C (PBS).  Treat as finished.
        if jobstat == "C":
            return False
        else:
            return True

    return False

######################################################################
def markCompletedTodoEntry(seriesCfg, precTsrc, todoList):
    """Update the todoList, change status to X"""

    key = seriesCfg + "-" + precTsrc
    todoList[key] = [ seriesCfg, precTsrc, "X" ]
    print("Marked cfg", seriesCfg, precTsrc, "completed")


#######################################################################
def decodeSeriesCfg(seriesCfg):
    """Decode series, cfg, as it appeaers in the todo file"""
    return seriesCfg.split(".")

#######################################################################
def decodePrecTsrc(seriesCfg):
    """Decode prec, tsrc, as it appeaers in the todo file
       Takes P.nn -> [P, nnn]"""
    return seriesCfg.split(".")

######################################################################
def purgeProps(param,seriesCfg):
    """Purge propagators for the specified configuration"""

    print("Purging props for", seriesCfg)
    series, cfg = decodeSeriesCfg(seriesCfg)
    configID = codeCfg(series, cfg)
    prop = param['files']['prop']
    subdirs = prop['subdirs'] + [ configID ]
    remotePath = os.path.join(*subdirs)
    cmd = ' '.join([ "nohup", "/bin/rm -r", remotePath, "> /dev/null 2> /dev/null &"])
    print(cmd)
    try:
        subprocess.call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't remove props.  Error code", e.returncode, ".")

######################################################################
def purgeRands(param,seriesCfg):
    """Purge random sources for the specified configuration"""

    print("Purging rands for", seriesCfg)
    series, cfg = decodeSeriesCfg(seriesCfg)
    configID = codeCfg(series, cfg)
    rand = param['files']['rand']
    subdirs = rand['subdirs'] + [ configID ]
    remotePath = os.path.join(*subdirs)
    cmd = ' '.join([ "nohup", "/bin/rm -r", remotePath, "> /dev/null 2> /dev/null &"])
    print(cmd)
    try:
        subprocess.call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't remove rands.  Error code", e.returncode, ".")

######################################################################
def tarInputPath(stream, s06Cfg, precTsrc):
    """Where the data and logs are found"""
    return os.path.join(stream, s06Cfg, precTsrc)

######################################################################
def purgeSymLinks(param, jobCase):
    """Purge symlinks for the specified jobID"""

    (stream, series, cfg, prec, tsrc, s06Cfg, tsrcID, jobID, jobSeqNo)  = jobCase

    print("Purging symlinks for job", jobID)

    io = param['files']['out']
    logsPath = os.path.join(tarInputPath(stream, s06Cfg, tsrcID), io['subdir'])
    cmd = ' '.join([ "find -P", logsPath, "-lname '?*Job'"+ jobID + "'*' -exec /bin/rm '{}' \;"])
    print(cmd)
    try:
        subprocess.call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: rmdir exited with code", e.returncode, ".")

######################################################################
def resetTodoEntry(seriesCfg, precTsrc, todoList):
    """Mark the todo entry for a job that did not complete"""

    print("Marking", seriesCfg, precTsrc, "for repairs.")
    key = seriesCfg + "-" + precTsrc
    todoList[key] = [ seriesCfg, precTsrc, "XXfix" ]

######################################################################
def goodCountCorrFiles(expectFiles, path):
    """Check the line count in a correlator file"""

    cmd = ' '.join([ "find", path, "-name '*corr*' -print | wc -l"])
    #    print(cmd)
    try:
        reply = subprocess.check_output(cmd, shell = True)
    except subprocess.CalledProcessError as e:
        print("ERROR: Can't count data entries")
        return False
    
    # Line count is first field
    foundFiles = int(reply.split()[0])

    if int(foundFiles) != int(expectFiles):
        print("ERROR: unexpected number of correlator files under", path,
              "expected", expectFiles, "found", foundFiles )
        return False

    return True

######################################################################
def goodDataLines(expectLines, corrPath):
    """Check the line count in a correlator file"""

    cmd = ' '.join([ "wc -l", corrPath])
    #    print(cmd)
    # Check the number of entries 
    try:
        reply = subprocess.check_output(cmd, shell = True)
    except subprocess.CalledProcessError as e:
        print("ERROR: Can't count data entries")
        return False
    
    # Line count is first field
    foundLines = int(reply.split()[0])
    
    if foundLines != expectLines:
        print("ERROR: incorrect line count in", corrPath,
              "expected", expectLines, "found", foundLines )
        return False

    return True
    
######################################################################
def goodData(param, jobCase):
    """Check that the data are complete"""

    (stream, series, cfg, prec, tsrc, s06Cfg, tsrcID, jobID, jobSeqNo)  = jobCase

    # Count correlator files
    expectFiles = int(param['outputCheck']['corrFiles'])
    corrDataDir = os.path.join(stream, s06Cfg, tsrcID, "data")
    if not goodCountCorrFiles(expectFiles, corrDataDir):
        return False

    # Check the files and their sizes against the fiducial list
    corrList = param['outputCheck']['corrFiducial']
    try:
        cfp = open(corrList)
    except:
        print("ERROR opening", corrList)
        return 1

    # Check the size of each required correlator file
    sys.stdout.write("Checking line counts..")
    sys.stdout.flush()
    progressCounter = 0
    for line in cfp:
        corrFile, expectLines = line.split()
        expectLines = int(expectLines)
        # Replace "CFG" with the actual configuration label
        corrFile = re.sub('CFG', s06Cfg, corrFile)
        corrPath = os.path.join(stream, s06Cfg, tsrcID, "data", corrFile)
        if not goodDataLines(expectLines, corrPath):
            return False

        progressCounter += 1
        if progressCounter % 500 == 0:
              sys.stdout.write(".")
              sys.stdout.flush()
    sys.stdout.write("OK\n")
    sys.stdout.flush()
    return True

######################################################################
def countPhrase(logPath, phrase):
    """Count occurrences of a phrase in a file"""
    
    cmd = "grep -w" + " \'" + phrase + "\' " + logPath + " | wc -l"
#    print(cmd)
    try:
        reply = subprocess.check_output(cmd, shell = True)
    except subprocess.CalledProcessError as e:
        print("Error checking for bad convergence")
        return False
    
    count = int(reply.split()[0])
    return count

######################################################################
def goodLogs(param, jobCase):
    """Check that the log files are complete"""

    (stream, series, cfg, prec, tsrc, s06Cfg, tsrcID, jobID, jobSeqNo)  = jobCase
    precTsrcConfigId = [ prec, tsrc, series, cfg ]

    for step in range(param['job']['steprange']['high']):
        expectFile = outFileName(stream, precTsrcConfigId, jobSeqNo, '', "step" + str(step))
        logPath = os.path.join(stream, s06Cfg, tsrcID, "logs", expectFile)
        try:
            stat = os.stat(logPath)
        except OSError:
            print("ERROR: Can't find expected output file", path)
            return False

        # Check for "RUNNING COMPLETED"
        entries = countPhrase(logPath, 'RUNNING COMPLETED')
        if entries < 1:
            print("ERROR: did not find 'RUNNING COMPLETED' in", logPath)
            return False

        # Check for nonconvergence, signaled by lines with "NOT"
        entries = countPhrase(logPath, "NOT")
        if entries > 0:
            print("WARNING: ", entries, "lines with 'NOT' suggesting nonconvergence")
#            return False
    
    # Passed these tests
    print("Output files OK")
    print("COMPLETE")

    return True

######################################################################
def tarFileName(tag, jobID, s06Cfg, tsrcID):
    """Construct tar file name"""
    return "Job{0:s}{1:s}_{2:s}_{3:s}.tar.bz2".format(tag, jobID, tsrcID, s06Cfg)

######################################################################
def tarFileDir(stream, s06Cfg):
    """Where we put the tar file"""
    return os.path.join(stream, s06Cfg, "tar")

######################################################################
def makeTar(stream, jobCase):
    """Create the tar file for a single source time"""

    (stream, series, cfg, prec, tsrc, s06Cfg, tsrcID, jobID, jobSeqNo)  = jobCase

    # Name of the tar file to be produced
    tarInput = tarInputPath(stream, s06Cfg, tsrcID)
    tarDir = tarFileDir(stream, s06Cfg)
    tarName = tarFileName('', jobID, s06Cfg, tsrcID)
    tarPath = os.path.join(tarDir, tarName)

    # Make sure the "tar" directory exists
    cmd = ' '.join(["mkdir -p", tarDir])
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't make directory", tarDir)
        return False

    # Gather the list of files to go into the tar file
    # All data files with matching configuration label for this cfg and source time
    fileList = "foo-tar"
    cmd = ' '.join(["pushd", tarInput, "; find data -name \'*"+s06Cfg+"\' -print >", fileList, "; popd"])
    print(cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't list data files in", fileList)
        return False

    # All log files with matching configuration label for this cfg and source time
    cmd = ' '.join(["pushd", tarInput, "; find logs -name \'*"+s06Cfg+"\' -print >>", fileList, "; popd"])
    print(cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't list log files in", fileList)
        return False

    # Create the bzipped tar file from the list
    fileListPath = os.path.join(tarInput, fileList)
    cmd = ' '.join(["tar -C ", tarInput, "-cjf ", tarPath, "-T ", fileListPath])
    print(cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't create", tarPath, "from", fileList)
        return False

    return True

######################################################################
def decodeCase(stream, seriesCfg, precTsrc, jobID, jobSeqNo):
    """Move failed output to temporary failure archive"""

    series, cfg = decodeSeriesCfg(seriesCfg)
    s06Cfg = codeCfg(series, cfg)
    prec, tsrc = decodePrecTsrc(precTsrc)
    tsrc = int(tsrc)
    tsrcID = codeTsrc(prec,tsrc)

    return stream, series, cfg, prec, tsrc, s06Cfg, tsrcID, jobID, jobSeqNo

######################################################################
def moveFailedOutputs(jobCase):
    """Move failed output to temporary failure archive"""
    
    (stream, series, cfg, prec, tsrc, s06Cfg, tsrcID, jobID, jobSeqNo)  = jobCase

    badOutputPath = tarInputPath(stream, s06Cfg, tsrcID)
    failPath = os.path.join(stream, s06Cfg, "fail", jobID)

    # Move the failed output
    cmd = " ".join(["mkdir -p ", failPath, "; mv", badOutputPath, failPath])
    print(cmd)
    try:
        subprocess.check_output(cmd, shell = True).decode("ASCII")
    except subprocess.CalledProcessError as e:
        status = e.returncode

######################################################################
def checkPendingJobs(YAMLAll, YAMLMachine, YAMLEns, YAMLLaunch):
    """Process all entries marked Q in the todolist"""

    # Read primary parameter file
    param = loadParamsJoin(YAMLEns, YAMLAll)

    paramMachine = loadParam(YAMLMachine)
    param = updateParam(param,paramMachine)

    paramLaunch = loadParam(YAMLLaunch)
    param = updateParam(param,paramLaunch)

    # Add to param the possible locations of output files we will check
    addRootPaths(param)

    # Read the todo file
    todoFile = param['nanny']['todofile']
    lockFile = lockFileName(todoFile)
    todoList = readTodo(todoFile, lockFile)

    changed = False
    for todoEntry in sorted(todoList,key=keyToDoEntries):
        a = todoList[todoEntry]
        if len(a) == 5:
            (seriesCfg, precTsrc, flag, jobID, jobSeqNo) = a
            if flag != "Q":
                continue
        else:
            continue
    
        print("------------------------------------------------------")
        print("Checking cfg", seriesCfg, precTsrc, "jobID", jobID, "jobSeqNo", jobSeqNo)
        print("------------------------------------------------------")

        stream = param['stream']
        jobCase = decodeCase(stream, seriesCfg, precTsrc, jobID, jobSeqNo)
        (stream, series, cfg, prec, tsrc, s06Cfg, tsrcID, jobID, jobSeqNo)  = jobCase

        # If job is still queued, skip this entry
        if jobStillQueued(param,jobID):
            continue

        # todo data will be changed
        changed = True

        # Check data files before tarring them up
        if goodData(param, jobCase) and goodLogs(param, jobCase):
            # Job appears to be complete
            markCompletedTodoEntry(seriesCfg, precTsrc, todoList)

            # Cleanup from complete and incomplete runs
            #        purgeProps(param,seriesCfg)
            #        purgeRands(param,seriesCfg)
            purgeSymLinks(param, jobCase)

            # Create tar file for this job from entries in the data and logs tree
            if not makeTar(stream, jobCase):
                print("ERROR: Couldn't create the tar file.")
                resetTodoEntry(seriesCfg, precTsrc, todoList)

        else:
            # If not complete, reset the todo entry
            resetTodoEntry(seriesCfg, precTsrc, todoList)

            # Salvage what we can
            cmd = " ".join(["../scripts/clean_corrs.py", stream,seriesCfg,precTsrc,"corr.fiducial"])
            print(cmd)
            try:
                reply = subprocess.check_output(cmd, shell = True).decode("ASCII")
                print(reply)
            except subprocess.CalledProcessError as e:
                status = e.returncode

            # Move the output from the failed run out of the way
            moveFailedOutputs(jobCase)
            
        sys.stdout.flush()

        # Take a cat nap (avoids hammering the login node)
        subprocess.check_call(["sleep", "1"])

    if changed:
        writeTodo(todoFile, lockFile, todoList)
    else:
        removeTodoLock(lockFile)

############################################################
def main():

    # Parameter file
    YAMLAll = "../scripts/params-allHISQ-plus5.yaml"
    YAMLMachine = "params-machine.yaml"
    YAMLEns = "params-ens.yaml"
    YAMLLaunch = "../scripts/params-launch.yaml"

    checkPendingJobs(YAMLAll, YAMLMachine, YAMLEns, YAMLLaunch)


############################################################
main()
