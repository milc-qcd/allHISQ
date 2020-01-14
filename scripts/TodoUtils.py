# Scripts supporting job queue management
# spawnjob.py and check_completed.py

# For Python 3 version

import sys, os, yaml, subprocess

######################################################################
def lockFileName(todoFile):
    """Directory entry"""
    return todoFile + ".lock"

######################################################################
def setTodoLock(lockFile):
    """Set lock file"""

    if os.access(lockFile, os.R_OK):
        print("Error. Lock file present. Quitting.")
        sys.exit(1)

    subprocess.call(["touch", lockFile])
    
######################################################################
def removeTodoLock(lockFile):
    """Remove lock file"""
    subprocess.call(["rm", lockFile])


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

######################################################################
def loadParam(file):
    """Read the YAML parameter file"""

    try:
        param = yaml.load(open(file,'r'))
    except subprocess.CalledProcessError as e:
        print("WARNING: loadParam failed for", e.cmd)
        print("return code", e.returncode)
        sys.exit(1)

    return param

######################################################################
def readTodo(todoFile, lockFile):
    """Read the todo file"""
    
    setTodoLock(lockFile)
    todoList = dict()
    try:
        with open(todoFile) as todo:
            todoLines = todo.readlines()
    except IOError:
        print("Can't open", todoFile)
        sys.exit(1)

    for line in todoLines:
        if len(line) == 1:
            continue
        a = line.split()
        todoList[a[0]] = a

    todo.close()
    return todoList

######################################################################
def keyToDoEntries(td):
    """Sort key for todo entries with format x.nnnn"""

    (stream, cfg) = td.split(".")
    return "{0:s}{1:010d}".format(stream, int(cfg))

######################################################################
def cmpToDoEntries(td1, td2):
    """Compare todo entries with format x.nnnn"""
    # Python 2.7 only

    (stream1, cfg1) = td1.split(".")
    (stream2, cfg2) = td2.split(".")

    # Sort first on stream, then on cfg
    order = cmp(stream1, stream2)
    if order == 0:
        order = cmp(int(cfg1), int(cfg2))

    return order

######################################################################
def writeTodo(todoFile, lockFile, todoList):
    """Write the todo file"""

    # Back up the files
    subprocess.call(["mv", todoFile, todoFile + ".bak"])

    try:
        todo = open(todoFile, "w")

    except IOError:
        print("Can't open", todoFile, "for writing")
        sys.exit(1)
            
    for line in sorted(todoList, key=keyToDoEntries):
        a = tuple(todoList[line])
        if len(a) == 4:
            print("{0:s} {1:s} {2:s} {3:s}".format(*a),file=todo)
        elif len(a) == 3:
            print("{0:s} {1:s} {2:s}".format(*a),file=todo)
        elif len(a) == 2:
            print("{0:s} {1:s}".format(*a),file=todo)
        elif len(a) == 1:
            print("{0:s}".format(*a),file=todo)

    todo.close()

    removeTodoLock(lockFile)
