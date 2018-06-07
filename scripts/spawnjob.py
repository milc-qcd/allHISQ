#! /usr/local/python2/bin/python2.7 -u

import sys, os, yaml, re, subprocess
from TodoUtils import *
from Cheetah.Template import Template

# Nanny script for managing job queues
# C. DeTar 

# Usage

# From the ensemble directory containing params-allHISQ.yaml and the
# todo file, do:
# ../scripts/spawnjob.py

# Requires a todo file with a list of configurations to be processed

# The todo file contains the list of jobs to be done.
# The line format of the todo file is
# <cfgno> [<flag> [<jobid>]]
# If the flag is empty, the job needs to be run
# If the flag is "X", the job has been finished
# If it is flagged "Q", the job was queued and <jobid> is present

# Requires params-allHISQ.yaml with definitions of variables needed here

######################################################################
def countQueue(  myjobname ):
    """Count my jobs in the queue"""

    user = os.environ['USER']
    cmd = ' '.join(["qstat -u", user, "| grep", user, "| grep", myjobname, "| wc -l"])
    nqueued = int(subprocess.check_output(cmd,shell=True))

    return nqueued

######################################################################
def nextCfgnos( maxCases, todoList ):
    """Get next sets of cfgnos from todo file"""

    # return status 1 failure, 0 success

    # Get the cfg number and source location 
    # of the next lattice from the todo file

    cfgnos = []
    for line in sorted(todoList):
        a = todoList[line]
        if len(a) == 1 or a[1] != "Q" and a[1] != "X" and a[1] != "XX":
            cfgnos.append(a[0])
            if len(cfgnos) >= maxCases:
                break

    ncases = len(cfgnos)
    
    if ncases > 0:
        print "Found", ncases, "cases...", cfgnos

    return cfgnos



######################################################################
# def nextQsubSeqno(file):
#     """Get our next qsub index"""
# 
#     try:
#         with open(file,"r") as qsubSeqFile:
#             lines = qsubSeqFile.readlines()
#     except IOError:
#         print "Can't open", file
#         sys.exit(1)
#     qsubSeqFile.close()
# 
#     qsubSeqNo = int(lines[0])
#     qsubSeqNo = qsubSeqNo + 1
# 
#     qsubSeqFile = open(file,"w")
#     print >>qsubSeqFile, qsubSeqNo
#     qsubSeqFile.close()
# 
#     return qsubSeqNo

######################################################################
def submitJob(param, cfgnos, pbsScript):
    """Submit the job"""

    layout = param['submit']['layout']
    njobs = layout['njobs']
    nodes = layout['basenodes'] * njobs
    np = nodes * layout['ppn']
    walltime = param['submit']['walltime']

    jobname = param['submit']['jobname']

    # qsubSeqNo = nextQsubSeqno("QSUBSEQNO")

    # Job parameters are included on the qsub line.
    # The are also written to a short file
    # in case the job submission system
    # doesn't support multiple parameters on the
    # qsub line

    # file = "variables" + str(qsubSeqNo) + ".sh"
    # varFile = open(file,"w")
    varlats = "LATS=" + "/".join(str(c) for c in cfgnos)
    varncases = "NCASES=" + str(len(cfgnos))
    varnjobs = "NJOBS=" + str(njobs)
    varnp = "NP=" + str(np)
    # print >>varFile, varlats
    # print >>varFile, varncases
    # print >>varFile, varnjobs
    # print >>varFile, varnp
    # 
    # varFile.close()

    varnodes = str(nodes)
    varwalltime = walltime

    try:
        stat = os.stat(pbsScript)
    except OSError:
        print "Can't find", pbsScript
        print "Quitting"
        sys.exit(1)

    cmd = [ "qsub", "-l", ",".join(["nodes="+varnodes, "walltime="+varwalltime]), "-N", jobname,
            "-v", ",".join([varlats,varncases,varnjobs,varnp]), pbsScript ]
    cmd = " ".join(cmd)

    print cmd
    reply = ""
    try:
        reply = subprocess.check_output(cmd, shell=True).splitlines()
    except subprocess.CalledProcessError as e:
        print reply
        print "qsub error.  Return code", e.returncode
        sys.exit(1)

    print reply

    # Get job ID (PBS version)
    # qsub reply format is
    # 3314170.kaon2.fnal.gov submitted
    # but we want just the number

    jobid = reply[0].split(".")[0]

    date = subprocess.check_output("date",shell=True).rstrip("\n")
    print date, "Submitted job", jobid, "for cfgs", cfgnos

    return (0, jobid)

######################################################################
def markQueuedTodoEntries(cfgnos, jobid, todoList):
    """Update the todoFile, change status to "Q" and mark the job number"""

    for cfg in cfgnos:
        todoList[cfg] = [ cfg, "Q", jobid ]

######################################################################
def nannyLoop(YAML):
    """Check job periodically and submit to the queue"""
    
    date = subprocess.check_output("date",shell=True).rstrip("\n")
    hostname = subprocess.check_output("hostname",shell=True).rstrip("\n")
    print date, "Spawn job process", os.getpid(), "started on", hostname

    param = loadParam(YAML)
    todoFile = param['nanny']['todofile']
    maxCases = param['nanny']['maxcases']
    njobs = param['submit']['layout']['njobs']
    pbsScript = param['submit']['pbsScript']
    lockFile = lockFileName(todoFile)

    # Keep going until
    #   we see a file called "STOP"
    #   we have exhausted the lis
    #   there are qsub or qstat errors

    while True:
        if os.access("STOP", os.R_OK):
            print "Spawn job process stopped because STOP file is present"
            break

        # Count queued jobs with our job name
        nqueued = countQueue( param['submit']['jobname'] )
  
        print "Found", nqueued, "jobs"

        # Submit until we have the desired number of jobs in the queue
        if nqueued < param['nanny']['maxqueue']:
            todoList = readTodo(todoFile, lockFile)

            # List a set of cfgnos
            cfgnos = nextCfgnos(maxCases, todoList)
            ncases = len(cfgnos)

            # If we have exhausted the todo list, stop
            if ncases <= 0:
                print "No more lattices. Nanny quitting."
                removeTodoLock(lockFile)
                sys.exit(0)

            # Submit the job
            ( status, jobid ) = submitJob(param, cfgnos, pbsScript)
            
            # Job submission succeeded
            # Edit the todoFile, marking the lattice queued and indicating the jobid
            if status == 0:
                markQueuedTodoEntries(cfgnos, jobid, todoList)
            else:
                # Job submission failed
                if status == 1:
                    # Fatal error
                    sys.exit(1)
                else:
                    print "Will retry submitting", cfgnos, "later"

            writeTodo(todoFile, lockFile, todoList)
            
        subprocess.call(["sleep", str( param['nanny']['wait'] ) ])

        # Reload parameters in case of changes
        param = loadParam(YAML)


############################################################
def main():

    # Parameter file
    YAML = "params-machine.yaml"
    nannyLoop(YAML)


############################################################
main()

