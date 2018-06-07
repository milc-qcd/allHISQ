#! /usr/local/python2/bin/python2.7 -u

import sys, os, yaml, re, subprocess, copy
from TodoUtils import *
from BpilnuFiles import *
from Cheetah.Template import Template

# Check job completion.  For any completed jobs, mark the todo list
# C. DeTar

# Usage

# From the ensemble directory containing params-Bpilnu.yaml and the
# todo file, do:
# ../../scripts/check_completed.py

# Requires a todo file with a list of configurations to be processed
# Requires a params-Bpilnu.yaml file with file parameters.

######################################################################
def jobStillQueued(jobid):
    """Get the status of the queued job"""
    # This code is locale dependent

    user = os.environ['USER']
    cmd = " ".join(["qstat", "-u", user, "|", "grep", jobid])
    reply = ""
    try:
        reply = subprocess.check_output(cmd, shell = True)
    except subprocess.CalledProcessError as e:
        status = e.returncode
        # If status is other than 0 or 1, we have a qstat problem
        # Treat job as unfinished
        if status != 1:
            print "qstat error", status, "Can't get the job status.  Skipping."
            return True

    if len(reply) > 0:
        a = reply.split()
        queueTime = a[8]
        jobstat = a[9]
        print "Job status", jobstat, "queue time", queueTime
        # If job is being canceled, jobstat = C.  Treat as finished.
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
    stream = param['files']['stream']
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

# ############################################################
# def updateParam(param, paramUpdate):
#     """Update the param dictionary according to terms in paramUpdate"""
# 
#     # Updating is recursive in the tree so we can update selected branches
#     # leaving the remainder untouched
#     for b in paramUpdate.keys():
#         try:
#             k = paramUpdate[b].keys()
#             n = len(k)
#         except AttributeError:
#             n = 0
# 
#         if b in param.keys() and n > 0:
#             # Keep descending until we run out of branches
#             updateParam(param[b], paramUpdate[b])
#         else:
#             # Then stop, replacing just the last branch or creating a new one
#             param[b] = paramUpdate[b]
# 
#     return param

######################################################################
# def makeParamSets(param):
#     """Create parameter sets for all tasks"""
# 
#     # Main 2pt and 3pt correlators
#     params = list([param])
# 
#     newparam = copy.deepcopy(param)
#     while True:
#         YAMLUpdate = newparam['paramSet']['nextParamUpdate']
#         if YAMLUpdate == None:
#             break
#         # Parameter file update
#         try:
#             paramUpdate = yaml.load(open(YAMLUpdate,'r'))
#         except:
#             print "ERROR: Error loading the parameter file", YAMLUpdate
#             sys.exit(1)
#         updateParam(newparam, paramUpdate)
#         params.append(newparam)
# 
#     # The KS parameter set if specified
#     newparam = copy.deepcopy(param)
#     YAMLKSUpdate = newparam['paramSet']['KSParamUpdate']
#     if YAMLKSUpdate != None:
#         try:
#             paramKSUpdate = yaml.load(open(YAMLKSUpdate,'r'))
#         except:
#             print "ERROR: Error loading the parameter file", YAMLKSUpdate
#             sys.exit(1)
#         updateParam(newparam, paramKSUpdate)
#         params.append(newparam)
# 
#     return params

######################################################################
def checkPendingJobs(YAML):
    """Process all entries marked Q in the todolist"""

    # Read primary parameter file
    param = loadParam(YAML)

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
    for todoEntry in todoList:
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
        print "Checking cfg", cfg, "jobID", jobid
        print "--------------------------------------"


        # If job is still queued, skip this entry
        if jobStillQueued(jobid):
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

        # Take a cat nap (avoids hammering the login node)
        subprocess.check_call(["sleep", "1"])

    if changed:
        writeTodo(todoFile, lockFile, todoList)
    else:
        removeTodoLock(lockFile)

############################################################
def main():

    # Parameter file
    YAML = "params-Bpilnu.yaml"

    checkPendingJobs(YAML)


############################################################
main()
