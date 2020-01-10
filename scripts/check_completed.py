#! /usr/bin/env python2.7

import sys, os, yaml, re, subprocess, copy
from TodoUtils import *
from allHISQFiles import *
from Cheetah.Template import Template

# Check job completion.  For any completed jobs, mark the todo list
# C. DeTar

# Usage

# From the ensemble directory containing params-allHISQ.yaml and the
# todo file, do:
# ../../scripts/check_completed.py

# Requires a todo file with a list of configurations to be processed
# Requires a params-allHISQ.yaml file with file parameters.

######################################################################
def jobStillQueued(param,jobid):
    """Get the status of the queued job"""
    # This code is locale dependent

    locale = param['submit']['locale']
    scheduler = param['launch'][locale]['scheduler']
    
    user = os.environ['USER']
    if scheduler == 'LSF':
        cmd = " ".join(["bjobs", "-u", user, "|", "grep", jobid])
    elif scheduler == 'PBS':
        cmd = " ".join(["qstat", "-u", user, "|", "grep", jobid])
    elif scheduler == 'SLURM':
        cmd = " ".join(["squeue", "-u", user, "|", "grep", jobid])
    elif scheduler == 'Cobalt':
        cmd = " ".join(["qstat", "-fu", user, "|", "grep", jobid])
    else:
        print "Don't recognize scheduler", scheduler
        print "Quitting"
        sys.exit(1)
    reply = ""
    try:
        reply = subprocess.check_output(cmd, shell = True)
    except subprocess.CalledProcessError as e:
        status = e.returncode
        # If status is other than 0 or 1, we have a qstat problem
        # Treat job as unfinished
        if status != 1:
            print "Error", status, "Can't get the job status.  Skipping."
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
            print "Don't recognize scheduler", scheduler
            print "Quitting"
            sys.exit(1)

        print "Job status", jobstat, field, "time", time
        # If job is being canceled, jobstat = C (PBS).  Treat as finished.
        if jobstat == "C":
            return False
        else:
            return True

    return False

######################################################################
def markCompletedTodoEntry(cfg, todoList):
    """Update the todoList, change status to X"""

    todoList[cfg] = [ cfg, "X" ]
    print "Marked cfg", cfg, "completed"


#######################################################################
def decodeSeriesCfg(seriesCfg):
    """Decode series, cfg, as it appeaers in the todo file"""
    return seriesCfg.split(".")

######################################################################
def purgeProps(param,cfg):
    """Purge propagators for the specified configuration"""

    print "Purging props for", cfg
    suffix, cfg = decodeSeriesCfg(cfg)
    configID = codeCfg(suffix, cfg)
    prop = param['files']['prop']
    subdirs = prop['subdirs'] + [ configID ]
    remotePath = os.path.join(*subdirs)
    cmd = ' '.join([ "nohup", "/bin/rm -r", remotePath, "> /dev/null 2> /dev/null &"])
    print cmd
    try:
        subprocess.call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print "ERROR: can't remove props.  Error code", e.returncode, "."

######################################################################
def purgeRands(param,cfg):
    """Purge random sources for the specified configuration"""

    print "Purging rands for", cfg
    suffix, cfg = decodeSeriesCfg(cfg)
    configID = codeCfg(suffix, cfg)
    rand = param['files']['rand']
    subdirs = rand['subdirs'] + [ configID ]
    remotePath = os.path.join(*subdirs)
    cmd = ' '.join([ "nohup", "/bin/rm -r", remotePath, "> /dev/null 2> /dev/null &"])
    print cmd
    try:
        subprocess.call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print "ERROR: can't remove rands.  Error code", e.returncode, "."

######################################################################
def purgeSymLinks(param,jobid):
    """Purge symlinks for the specified jobid"""

    print "Purging symlinks for job", jobid
    io = param['files']['out']
    cmd = ' '.join([ "find -P", os.path.join(param['stream'],io['subdir']), "-lname '?*Job'"+ jobid + "'*' -exec /bin/rm '{}' \;"])
    print cmd
    try:
        subprocess.call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print "ERROR: rmdir exited with code", e.returncode, "."

######################################################################
def resetTodoEntry(cfg, todoList):
    """Reset the todo entry for a job that did not complete"""

    print "Resetting", cfg, "for a retry."
    todoList[cfg] = [ cfg ]

######################################################################
def getTarPath(param, jobid, cfg):
    """The tarball file name for the job"""
    
    file = param['files']['tar']
    root = param['files']['root']
    stream = param['stream']
#    tag = param['paramSet']['tag']
    tag = ''

    tarPath = os.path.join( root[file['root']], stream )

    configId = cfg.split(".")
    name = tarFileName(configId, jobid, tag)

    return (tarPath, name)

######################################################################
def fullTarFileName(param, jobid, cfg):
    """Name including path"""

    (tarPath, name) = getTarPath(param, jobid, cfg)
    return os.path.join(tarPath, name)


######################################################################
def getTarFailPath(param, jobid, cfg):
    """Name including path"""

    (tarPath, name) = getTarPath(param, jobid, cfg)
    path = os.path.join(tarPath, "fail")
    makePath(path)
    return path


######################################################################
def moveFailureFiles(tarFile, tarFailPath):
    """Move incomplete files for a job that did not complete"""

    if os.access(tarFile, os.R_OK):
        try:
            subprocess.check_output(["mv", tarFile, tarFailPath])
        except subprocess.CalledProcessError as e:
            print "Error", e.returncode, "moving", tarFile, "to", tarFailPath

######################################################################
def getTarGoodPath(param, jobid, cfg):
    """Name including path"""

    (tarPath, name) = getTarPath(param, jobid, cfg)
    path = os.path.join(tarPath, "tar")
    makePath(path)
    return path


######################################################################
def moveGoodFiles(tarFile, tarGoodPath):
    """Move incomplete files for a job that did not complete"""

    if os.access(tarFile, os.R_OK):
        try:
            subprocess.check_output(["mv", tarFile, tarGoodPath])
        except subprocess.CalledProcessError as e:
            print "Error", e.returncode, "moving", tarFile, "to", tarGoodPath

######################################################################
def checkComplete(param, tarFile):
    """Check that output file is complete"""

    # We check the file size
    try:
        reply = subprocess.check_output(["ls", "-l", tarFile])
    except subprocess.CalledProcessError as e:
        print "Error", e.returncode, "stat'ing output tar file", tarFile
        return False

    # File size in bytes is the 5th field in ls -l
    tarFileSize = int(reply.split()[4])
    tarFileGood = param['tarCheck']['tarbzip2Size']
    # Allow for a 5% variation
    
    if tarFileSize*1.05 < tarFileGood:
        print "ERROR: too small:", tarFile, "size", tarFileSize
        return False

    # We check the number of entries in the tar file
    try:
        reply = subprocess.check_output("tar -tjf " + tarFile + "| wc -l", shell = True)
    except subprocess.CalledProcessError as e:
        print "Error tar-listing", tarFile
        return False
    
    # Entry count is first field
    entries = int(reply.split()[0])
    entriesGood = param['tarCheck']['tarEntries']
    
    if entries < param['tarCheck']['tarEntries']:
        print "ERROR: missing entries: tar file", tarFile, "entry count", entries
        return False

    # We check for nonconvergence, signaled by lines with "NOT"
    try:
        reply = subprocess.check_output("tar -Oxjf " + tarFile + " logs | grep NOT | wc -l", shell = True)
    except subprocess.CalledProcessError as e:
        print "Error checking for bad convergence", tarFile
        return False
    entries = int(reply.split()[0])

    if entries > 0:
        print "ERROR: ", entries, "lines with 'NOT'"
        # Earlier versions of ks_spectrum_hisq reported spurious "NOT converged."
        if re.search("outJobKS",tarFile) == None:
            return False

    # Passed these tests
    print "COMPLETE: Output tar file", tarFile

    return True

######################################################################
def checkPendingJobs(YAMLMachine,YAMLEns,YAMLLaunch):
    """Process all entries marked Q in the todolist"""

    # Read primary parameter file
    param = loadParam(YAMLMachine)

    paramEns = loadParam(YAMLEns)
    param = updateParam(param,paramEns)

    paramLaunch = loadParam(YAMLLaunch)
    param = updateParam(param,paramLaunch)

    # Add to param the possible locations of output files we will check
    addRootPaths(param)

    # Read the todo file
    todoFile = param['nanny']['todofile']
    lockFile = lockFileName(todoFile)
    todoList = readTodo(todoFile, lockFile)

    # Create parameter sets for all job steps
#    params = makeParamSets(param)
    params = [param]

    changed = False
    for todoEntry in sorted(todoList,cmpToDoEntries):
        a = todoList[todoEntry]
        if len(a) == 3:
            (cfg, flag, jobid) = a
            if flag != "Q":
                continue
        else:
            continue
        if flag != "Q":
            continue
    
        print "--------------------------------------"
        print "Checking cfg", cfg, "jobid", jobid
        print "--------------------------------------"


        # If job is still queued, skip this entry
        if jobStillQueued(param,jobid):
            continue

        changed = True

        tarFiles = list()
        # Check tar balls for all job steps
        complete = True
        for p in params:
            tarFailPath = getTarFailPath(p, jobid, cfg)
            tarGoodPath = getTarGoodPath(p, jobid, cfg)
            tarFile = fullTarFileName(p, jobid, cfg)
            tarFiles.append(tarFile)
            if not checkComplete(p, tarFile):
                complete = False

        if complete:
            # Mark the todo entry completed
            markCompletedTodoEntry(cfg, todoList)
            # Move all tar balls to the good directory
            for tarFile in tarFiles:
                moveGoodFiles(tarFile, tarGoodPath)
        else:
            # If not complete, reset the todo entry and move all tar
            # balls to the failure directory
            resetTodoEntry(cfg, todoList)
            for tarFile in tarFiles:
                moveFailureFiles(tarFile, tarFailPath)

        # Cleanup from complete and incomplete runs
        purgeProps(param,cfg)
        purgeRands(param,cfg)
        purgeSymLinks(param,jobid)

        # Take a cat nap (avoids hammering the login node)
        subprocess.check_call(["sleep", "1"])

    if changed:
        writeTodo(todoFile, lockFile, todoList)
    else:
        removeTodoLock(lockFile)

############################################################
def main():

    # Parameter file
    YAMLMachine = "params-machine.yaml"
    YAMLEns = "params-ens.yaml"
    YAMLLaunch = "../scripts/params-launch.yaml"

    checkPendingJobs(YAMLMachine, YAMLEns, YAMLLaunch)


############################################################
main()
