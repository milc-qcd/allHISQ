# Scripts supporting job queue management
# spawnjob.py and check_completed.py

import sys, os, yaml, re, subprocess
from StringIO import StringIO
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

######################################################################
def lockFileName(todoFile):
    """Directory entry"""
    return todoFile + ".lock"

######################################################################
def setTodoLock(lockFile):
    """Set lock file"""

    if os.access(lockFile, os.R_OK):
        print "Error. Lock file present. Quitting."
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

############################################################
def loadParam(YAML):
    """Load a YAML parameter file"""

    # Initial parameter file
    try:
        param = yaml.load(open(YAML,'r'))
    except:
        print "ERROR: Error loading the parameter file", YAML
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
        print "Can't open", todoFile
        sys.exit(1)

    for line in todoLines:
        if len(line) == 1:
            continue
        a = line.split()
        todoList[a[0]] = a

    todo.close()
    return todoList

######################################################################
def cmpToDoEntries(td1, td2):
    """Compare quark keys.  This order is for multimass KS"""

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
        print "Can't open", todoFile, "for writing"
        sys.exit(1)
            
    for line in sorted(todoList, cmpToDoEntries):
        a = tuple(todoList[line])
        if len(a) == 4:
            print >>todo, "%s %s %s %s" % a
        elif len(a) == 3:
            print >>todo, "%s %s %s" % a
        elif len(a) == 2:
            print >>todo, "%s %s" % a
        elif len(a) == 1:
            print >>todo, "%s" % a

    todo.close()

    removeTodoLock(lockFile)

######################################################################
def concatenate(files):
    """Concatenate a list of files into a StringIO object."""
    out = StringIO()
    for file in files:
        with open(file, 'r') as f:
            out.writelines(f.readlines())
            out.write('\n')
    out.seek(0)
    return out

############################################################
class UniqueKeyLoader(yaml.Loader):
    """YAML loader class that checks for duplicate keys."""
    # copy of PyYAML:constructor.construct_mapping until next comment
    def construct_mapping(self, node, deep=False):
        if not isinstance(node, MappingNode):
            raise ConstructorError(None, None,
                    "expected a mapping node, but found %s" % node.id,
                    node.start_mark)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise ConstructorError("while constructing a mapping", node.start_mark,
                       "found unacceptable key (%s)" % exc, key_node.start_mark)
            # check for duplicate keys
            if key in mapping:
                raise ConstructorError("while constructing a mapping", node.start_mark,
                       "found duplicate key", key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

######################################################################
def readParams(files, errParse=True, unique=True):
    """Load a set of YAML parameter files into a single dictionary.
    First file in list should contain global YAML references."""
    filestring = concatenate(files)
    if not unique:
        return yaml.load(filestring)
    try:
        return yaml.load(filestring, UniqueKeyLoader)
    except ConstructorError, error:
        if not errParse:
            raise error
        else: # parse output error to better accommodate traceback
            duplicates = [int(i.split()[-1]) for i in re.findall(re.compile(r'line \d+'), str(error))]
            filestring.seek(0)
            duplicate = filestring.readlines()[duplicates[-1] - 1].strip()
            raise ValueError('yaml references taken from ' + files[0] +
                             '.\nFound duplicate key:\n' + duplicate)
