#! /usr/bin/env python

# Python 3 version

import sys, os, yaml, re, subprocess
from MILCprompts import *
from allHISQKeys import *
from allHISQFiles import *
from Cheetah.Template import Template

from datetime import datetime

######################################################################
def listMass(param, qk):
    """ Get the masses or kappas for the specified quark"""

    q = param['quarks'][qk]
    if q['type'] == 'clover':
        return q['kappa']
    elif q['type'] == 'KS':
        return q['mass']
                            
#######################################################################
def decodeSeriesCfg(seriesCfg):
    """Decode series, cfg, as it appeaers in the todo file
       Takes x.nnn -> [x, nnn]"""
    return seriesCfg.split(".")

#######################################################################
def decodePrecTsrc(seriesCfg):
    """Decode prec, tsrc, as it appeaers in the todo file
       Takes P.nn -> [P, nnn]"""
    return seriesCfg.split(".")

#######################################################################
def encodeSeriesCfgPrecSrc(seriesCfg,prec,tsrc):
    """Encode series, cfg, tsrc, prec
       takes x.nnn, P, mmm -> x.nnn.P.mmm """
    series, cfg = decodeSeriesCfg(seriesCfg)
    return ".".join([series, cfg, tsrc, prec])

#######################################################################
def decodeSeriesCfgPrecSrc(seriesCfgSrc,prec):
    """Decode series, cfg, prec, src
       takes x.nnn.P.mmm -> [x, nnn, P, mmm]"""
    return seriesCfgSrc.split(".")

######################################################################
def stageLattice(param, suffix, cfg):
    """Stage the lattice file"""

    ensemble = param['ensemble']
    run = ensemble['run']
    lat = param['files']['latCoul']

    root = param['files']['root']
    localRoot = root['local']

    fileCmd = param['fileCmd']

    # We don't need Coulomb gauge fixing for this project.
    # However, if we are loading propagators saved from the HISQ superscript
    # we need the Coulomb gauge-fixed file and the random number source
    # that go with the saved propagator
    name = latFileCoul( run, suffix, cfg )
    latCoul = StageFile( localRoot, None, root[lat['root']], 
                         lat['subdirs'], name, 'r', None, None, False )
    inLat = latCoul
    loadLat = (fileCmd['lat']['load'], inLat.path())
    saveLat = ('forget',)
    gFix = 'no_gauge_fix'
    
    if not latCoul.exist():
        name = latFileMILCv5( run, suffix, cfg)
        lat = param['files']['latMILCv5']
        latMILCv5 = StageFile( localRoot, None, root[lat['root']], 
                               lat['subdirs'], name, 'r', None, None, False )
        inLat = latMILCv5
        loadLat = (fileCmd['lat']['load'], inLat.path())
#        See explanation above.
#        saveLat = (fileCmd['lat']['save'], latCoul.path())
#        gFix = 'coulomb_gauge_fix'
        gFix = 'no_gauge_fix'  # Force use of the v5 lattice
        saveLat = ('forget',) # and don't save a copy.
        if not latMILCv5.exist():
            print("ERROR: lattice", inLat.path(), "not found")
            if param['scriptDebug'] != 'debug':
                sys.exit(1)

    return (latCoul, loadLat, saveLat, gFix)

######################################################################
def stageEigen(param, suffix, cfg):
    """Stage the eigenvector file"""

    ensemble = param['ensemble']
    run = ensemble['run']
    eig = param['files']['eigen']

    root = param['files']['root']
    localRoot = root['local']

    name = latFileEig( run, suffix, cfg )
    inEigen = StageFile( localRoot, None, root[eig['root']], eig['subdirs'], 
                         name, 'r', None, None, False )

    fileCmd = param['fileCmd']
    loadEigen = (fileCmd['eig']['load'], inEigen.path())
    saveEigen = ('forget_ks_eigen',)                   

    return inEigen, loadEigen, saveEigen

######################################################################
def fetchWF(param):
    """Fetch the wave function file"""
    wf = param['files']['wavefunction']
    name = wf['1S']
    root = param['files']['root']
    localRoot = root['local']
    wf1S = StageFile( localRoot, None, root[wf['root']], wf['subdirs'], 
                      name, 'r', None, None, False )
    if not wf1S.exist():
        if param['scriptDebug'] != 'debug':
            print("ERROR: Can't get wavefunction file.")
            sys.exit(1)
    return wf1S

######################################################################
def prepareRandomSource(param, precTsrcConfigId):
    """Fetch or prepare to generate the random wall source"""

    (prec, tsrc, suffix, cfg) = precTsrcConfigId

    # Random source files for spectator and daughter
    root = param['files']['root']
    localRoot = root['local']

    ensemble = param['ensemble']
    run = ensemble['run']

    rand = param['files']['rand']
    if rand['coherent'] == 'yes':
        # Files must exist
        name = rndFile('', run, precTsrcConfigId)
        rndDq = StageFile( localRoot, None, root[rand['root']], rand['subdirs'], 
                           name, 'r', None, None, False )
        name = rndFile('Sq', run, precTsrcConfigId)
        rndSq = StageFile( localRoot, None, root[rand['root']], rand['subdirs'], 
                           name, 'r', None, None, False )
        if not rndDq.exist() or not rndSq.exist():
            print("ERROR: with coherent random sources",rndDq.name(),"and",rndSq.name(),"must exist")
            if param['scriptDebug'] != 'debug':
                sys.exit(1)
    else:
        name = rndFile('', run, precTsrcConfigId)
        # Store random sources in subdirectories labeled by the configuration ID
        configID = codeCfg(suffix, cfg)
        remotePath = rand['subdirs'] + [configID]

#        rndDq = StageFile( localRoot, None, root[rand['root']], rand['subdirs'], name, 'x', None, False )
#        rndSq = StageFile( localRoot, None, root[rand['root']], rand['subdirs'], name, 'x', None, False )
        rndDq = StageFile( localRoot, None, root[rand['root']], remotePath, 
                           name, 'r', None, None, False )
        rndSq = StageFile( localRoot, None, root[rand['root']], remotePath, 
                           name, 'r', None, None, False )
    
    # With coherent sources we must distinguish the spectator and daughter random sources
    # Equivalent to antiquark and quark random sources
    # These strings become part of the quark key that uniquely identifies the propagator
    if rand['coherent'] == 'yes':
        rndQ = 'Sq'
        rndAq = 'Dq'
    else:
        rndQ = 'q'
        rndAq = 'q'

    return (rndSq, rndDq, rndQ, rndAq)

######################################################################
def compile2ptCorrelators(param, correlators, quarkKeys, rndQ, rndAq, nstep, precTsrcConfigId):
    """Parse the YAML 2pt parameters and make tables of propagators to
    be generated and 2pt correlators to be computed"""

    (prec, tsrc, suffix, cfg) = precTsrcConfigId

    root = param['files']['root']
    localRoot = root['local']
    residQuality = prec

    configId = codeCfg(suffix, cfg)
    tsrcId = codeTsrc(prec, tsrc)

    ensemble = param['ensemble']
    run = ensemble['run']
    stream = param['stream']
    
    corr2pts = param['corr2pts']
    for nptKey in corr2pts:
        if corr2pts[nptKey]['step'] != nstep:
            continue

        # Make a table of all the correlator attributes keyed by momentum
        # This information is used to construct the "correlator" lines
        corrAttrsTable = dict()
        for (p, stSnk, mom) in corr2pts[nptKey]['correlators']:
            momKey = makeMomKey(mom)
            if momKey not in corrAttrsTable.keys():
                corrAttrsTable[momKey] = list()
            prefix = prefix2pt(param['corrKey']['prefix'], stSnk)
            corrAttrsTable[momKey].append([prefix, p, stSnk])
    
        # Quark carries the momentum
        # Make a table of quark keys encoding the needed quark attributes
        (qk, smQSrcList, smQSnkList) = corr2pts[nptKey]['Q']
        for smQSrc in smQSrcList:
            for smQSnk in smQSnkList:
                for (p, stSnk, mom) in corr2pts[nptKey]['correlators']:
                    quark = param['quarks'][qk]
                    for m, eps in zip(quark['mass'], quark['naik_epsilon']):
                        qKey = makeQuarkKey((residQuality, qk, m, eps, rndQ, 
                                             makeSrcKey((smQSrc, makeMomKey(mom))), smQSnk))
                        appendUnique(quarkKeys, qKey)
    
        # Antiquark always zero momentum
        # Make a table of antiquark keys encoding the needed quark attributes
        (aQk, smAQSrcList, smAQSnkList) = corr2pts[nptKey]['aQ']
        mom = [0, 0, 0]
        for smAQSrc in smAQSrcList:
            for smAQSnk in smAQSnkList:
                quark = param['quarks'][aQk]
                for m, eps in zip(quark['mass'], quark['naik_epsilon']):
                    aQKey = makeQuarkKey((residQuality, aQk, m, eps, rndAq, 
                                          makeSrcKey((smAQSrc, makeMomKey(mom))), smAQSnk))
                    appendUnique(quarkKeys, aQKey)
    
        # Set up 2pt correlators
        # Result is a 2pt hadron "correlators" table with all needed attributes
        name = corr2ptFileName(nptKey, run, precTsrcConfigId)
        corr = param['files']['corr']
        (qk, smQSrcList, smQSnkList) = corr2pts[nptKey]['Q']
        (aQk, smAQSrcList, smAQSnkList) = corr2pts[nptKey]['aQ']
        for smAQSrc in smAQSrcList:
            for smQSrc in smQSrcList:
                for smQSnk in smQSnkList:
                    for smAQSnk in smAQSnkList:
                        quark = param['quarks'][aQk]
                        for mAq, epsAq in zip(quark['mass'], quark['naik_epsilon']):
                            mom = [0, 0, 0]
                            aQKey = makeQuarkKey((residQuality, aQk, mAq, epsAq, rndAq, 
                                                  makeSrcKey((smAQSrc, makeMomKey(mom))), smAQSnk))
                            for momKey in corrAttrsTable.keys():
                                quark = param['quarks'][qk]
                                for mQ, epsQ in zip(quark['mass'], quark['naik_epsilon']):
                                    qKey = makeQuarkKey((residQuality, qk, mQ, epsQ, rndQ, 
                                                         makeSrcKey((smQSrc, momKey)), smQSnk))
                                    mom = splitMomKey(momKey)
                                    mQkLab = massLabel(param['quarks'][qk], mQ)
                                    mAQkLab = massLabel(param['quarks'][aQk], mAq)
                                    massMomDir = massSubdir2pt(mQkLab, mAQkLab, mom)
                                    subDirs = [stream, configId, tsrcId, corr['subdir'], nptKey, massMomDir]
                                    
                                    corrFile = StageFile(localRoot, subDirs, root[corr['root']], 
                                                         subDirs, name, 'w', None, None, False)
                                    correlators.append([corrFile, qKey, aQKey, mom, corrAttrsTable[momKey]])
                                    
######################################################################
def compile3ptCorrelators(param, correlators, quarkKeys, rndQ, rndAq, nstep, precTsrcConfigId):
    """Parse the YAML 3pt parameters and make tables of propagators to
    be generated and 3pt correlators to be computed"""

    (prec, tsrc, suffix, cfg) = precTsrcConfigId

    root = param['files']['root']
    localRoot = root['local']

    configId = codeCfg(suffix, cfg)
    tsrcId = codeTsrc(prec, tsrc)

    ensemble = param['ensemble']
    run = ensemble['run']
    stream = param['stream']
    residQuality = prec
    
    corr3pts = param['corr3pts']
    for nptKey in corr3pts:
        if corr3pts[nptKey]['step'] != nstep:
            continue

        # Daughter: at current (sink) not smeared and always rotated if
        # clover. Momenta are injected at daughter
        (qk, smDSrcList) = corr3pts[nptKey]['Dq']
        if param['quarks'][qk]['type'] == 'KS':
            smDSnk = 'd'
        else:
            smDSnk = 'rot'
        for smDSrc in smDSrcList:
            for (p, stC, mom) in corr3pts[nptKey]['correlators']:
                quark = param['quarks'][qk]
                for m, eps in zip(quark['mass'], quark['naik_epsilon']):
                    daughterKey = makeQuarkKey((residQuality, qk, m, eps, rndAq, 
                                                makeSrcKey((smDSrc, makeMomKey(mom))), smDSnk))
                    appendUnique(quarkKeys, daughterKey)
    
        # Parent: at current (sink) not smeared and always rotated if clover
        qkP = corr3pts[nptKey]['Pq'][0]
    
        # Spectator: extended source (sink) smearing is done 
        # separately, no rotation, zero momentum at source
        (qkS, smSSrcList) = corr3pts[nptKey]['Sq']
        (qkD, smDSrcList) = corr3pts[nptKey]['Dq']
        smSSnk = 'ext'
        stP = corr3pts[nptKey]['spinTasteParent']
        try:
            select = corr3pts[nptKey]['select']
        except KeyError:
            select = 'all'
        for smDSrc in smDSrcList:
            for smSSrc in smSSrcList:
                for extT in corr3pts[nptKey]['extT']:
                    corr = param['files']['corr']
                    name = corr3ptFileName(nptKey, run, extT, precTsrcConfigId)
                    quarkP = param['quarks'][qkP]
                    for mQkP, epsP in zip(quarkP['mass'], quarkP['naik_epsilon']):
                        snkKey = makeSnkKey((smSSnk, str(extT), stP, qkP, mQkP, epsP))
        
                        # Tabulate the listed correlator attributes according to momentum
                        corrAttrsTable = dict()
                        for (p, stC, mom) in corr3pts[nptKey]['correlators']:
                            momKey = makeMomKey(mom)
                            if momKey not in corrAttrsTable.keys():
                                corrAttrsTable[momKey] = list()
                            mQkPLab = massLabel(param['quarks'][qkP], mQkP)
                            prefix = prefix3pt(param['corrKey']['prefix'], stP, stC, extT, mQkPLab)
                            corrAttrsTable[momKey].append([prefix, p, stC])
        
                        quark = param['quarks'][qkS]
                        for mQkS, epsS in zip(quark['mass'], quark['naik_epsilon']):
                            mom = [0, 0, 0]
                            parentKey = makeQuarkKey((residQuality, qkS, mQkS, epsS, rndQ, 
                                                      makeSrcKey((smSSrc, makeMomKey(mom))), snkKey))
                            appendUnique(quarkKeys, parentKey)
                            for momKey in corrAttrsTable.keys():
                                quark = param['quarks'][qkD]
                                for mQkD, epsD in zip(quark['mass'], quark['naik_epsilon']):
                                    # Provision for doing only the diagonal mass case: skip off diagonal
                                    if select == 'diagonal' and ( mQkD != mQkP or epsD != epsP ):
                                        continue
                                    daughterKey = makeQuarkKey((residQuality, qkD, mQkD, epsD, rndAq, 
                                                                makeSrcKey((smDSrc, momKey)), smDSnk))
                                    mom = splitMomKey(momKey)
                                    quark = param['quarks'][qkP]
                                    # Do we need support for multiple parent masses??
                                    mQkPLab = massLabel(param['quarks'][qkP], mQkP)
                                    mQkSLab = massLabel(param['quarks'][qkS], mQkS)
                                    mQkDLab = massLabel(param['quarks'][qkD], mQkD)
                                    massMomDir = massSubdir3pt(mQkPLab, mQkSLab, mQkDLab, mom)
                                    subDirs = [stream, configId, tsrcId, corr['subdir'], nptKey, massMomDir]
                                    corrFile = StageFile(localRoot, subDirs, root[corr['root']], 
                                                         subDirs, name, 'w', None, None, False)
                                    correlators.append([corrFile, daughterKey, parentKey, mom, corrAttrsTable[momKey]])

    
############################################################
def redirectStdoutStderr(file):
    """Redirect script stderr and stdout to a file"""
    
    # Open the log file
    so = se = open(file, 'a', 0)

    print("stdout and stderr will be redirectred to", file)
    
    # Re-open stdout without buffering
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    
    # Redirect stdout and stderr to the log file opened above
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    
######################################################################
def setUpJobTarFile(param, configId):
    """Define and open the tar file"""

    root = param['files']['root']
    localRoot = root['local']

    ensemble = param['ensemble']
    stream = param['stream']
    jobid = param['job']['id']
    tag = ''

    io = param['files']['tar']
    name = tarFileName(configId, jobid, tag)
    localpath = os.path.join( root[io['root']] )
    subDirs = [stream]
    tar = StageFile(localRoot, subDirs, localpath, subDirs, 
                    name, 'w', None, None, False)

    return tar
    
######################################################################
def setUpJobIOFiles(param, nstep, precTsrcConfigId, precTsrcConfigIdSym, kjob, njobs):
    """Define and open the stdin file, define stdout and stderr and redirect the script stdout, stderr"""

    (prec, tsrc, suffix, cfg) = precTsrcConfigId
    (precSym, tsrcSym, suffixSym, cfgSym) = precTsrcConfigIdSym

    root = param['files']['root']
    localRoot = root['local']

    ensemble = param['ensemble']
    run = ensemble['run']
    stream = param['stream']
    jobid = param['job']['id']

    step = 'step' + str(nstep)
    tag = ''

    configId = codeCfg(suffix, cfg)
    tsrcId = codeTsrc(prec,tsrc)

    configIDSym = codeCfg(suffixSym, cfgSym)
    tsrcIDSym = codeTsrc(precSym,tsrcSym)

    io = param['files']['log']
    # The logfile isn't doing its job -- needs fixing or removing
    name = logFileName(run, precTsrcConfigId, jobid, tag, step)
    multiJobName = logFileSymLink(run, precTsrcConfigIdSym, jobid, tag, step, kjob, njobs)
    multiJobSubDirs = [stream, configIDSym, tsrcIDSym, io['subdir']]
    localpath = os.path.join( root[io['root']] )
    # Don't stage the log file.  It contains script information
    # that might be needed in case the job fails.
    subDirs = [stream, configId, tsrcId, io['subdir']]
    stdlog = StageFile(None, None, localpath, subDirs, name, 'w', multiJobSubDirs, multiJobName, True)
    # Redirect script stdout and stderr to the log file
#    if param['scriptDebug'] != 'debug':
#        redirectStdoutStderr(stdlog.path())

    io = param['files']['in']
    name = inFileName(run, precTsrcConfigId, jobid, tag, step)
    multiJobName = inFileSymLink(run, precTsrcConfigIdSym, jobid, tag, step, kjob, njobs)
    multiJobSubDirs = [stream, configIDSym, tsrcIDSym, io['subdir']]
    localpath = os.path.join( root[io['root']] )
    subDirs = [stream, configId, tsrcId, io['subdir']]
    stdin = StageFile(localRoot, subDirs, localpath, subDirs, name, 
                      'w', multiJobSubDirs, multiJobName, True)

    io = param['files']['out']
    name = outFileName(run, precTsrcConfigId, jobid, tag, step)
    multiJobName = outFileSymLink(run, precTsrcConfigIdSym, jobid, tag, step, kjob, njobs)
    multiJobSubDirs = [stream, configIDSym, tsrcIDSym, io['subdir']]
    localpath = os.path.join( root[io['root']] )
    subDirs = [stream, configId, tsrcId, io['subdir']]
    stdout = StageFile(localRoot, subDirs, localpath, subDirs, name, 
                       'w', multiJobSubDirs, multiJobName, True)
    
    io = param['files']['err']
    name = errFileName(run, precTsrcConfigId, jobid, tag, step)
    multiJobName = errFileSymLink(run, precTsrcConfigIdSym, jobid, tag, step, kjob, njobs)
    multiJobSubDirs = [stream, configIDSym, tsrcIDSym, io['subdir']]
    localpath = os.path.join( root[io['root']] )
    subDirs = [stream, configId, tsrcId, io['subdir']]
    stderr = StageFile(localRoot, subDirs, localpath, subDirs, name, 'w', 
                       multiJobSubDirs, multiJobName, True)

    return (stdin, stdout, stderr, stdlog)
    
######################################################################
def initializePrompts(param, precTsrcConfigId):
    """Start input parameter set"""

    (prec, tsrc, suffix, cfg) = precTsrcConfigId

    ensemble = param['ensemble']
    dim = ensemble['dim']
    seed = str(cfg)+str(tsrc)

    # Label in header of input parameter file
    if param['scriptDebug'] == 'debug':
        jobID = 'JOBID'
    else:
        jobID = param['job']['id']

    layoutSciDAC = param['submit']['layout']['layoutSciDAC']
    work = ks_spectrum('test', dim, seed, jobID, layoutSciDAC)

    return work

######################################################################
def startGauge(param, work, loadLat, saveLat, gFix):
    """Start input parameter set"""

    uOrigin = [ 0, 0, 0, 0 ]
    bc = param['KSaction']['bc']
    u0 = param['ensemble']['u0']

    work.newGauge(Gauge(loadLat, u0, gFix, saveLat, param['apelink'], uOrigin, bc))

######################################################################
def addEigen(param, work, loadEigen, saveEigen):
    """Add eigenpair stanza"""

    Nvecs = param['eigen']['Nvecs']

    eigs = Eigen(loadEigen, Nvecs, saveEigen)
    work.newEigen(eigs)

######################################################################
def createSSDList(jobid):
    """Create the SSDList file"""

    cmd = ['touch', "SSDList." + jobid]
    cmd = ' '.join(cmd)
    print("#", cmd)
    try:
        subprocess.check_output(cmd, shell = True)
    except subprocess.CalledProcessError as e:
        print("ERROR adding", fileName, "to SSDlist")
    return

######################################################################
def updateSSDList(fileName, jobid):
    """Add a new file name to the SSDList"""

    cmd = ['echo', fileName, ">> SSDList." + jobid]
    cmd = ' '.join(cmd)
    print("#", cmd)
    try:
        subprocess.check_output(cmd, shell = True)
    except subprocess.CalledProcessError as e:
        print("ERROR adding", fileName, "to SSDlist")
    return
    
######################################################################
def checkSSDList(fileName, jobid):
    """Check SSDList to see if a file should now exist"""

    cmd = ['grep', fileName, "SSDList." + jobid, "> /dev/null"]
    cmd = ' '.join(cmd)
    print("#", cmd)
    try:
        lines = subprocess.check_output(cmd, shell = True).splitlines()
    except subprocess.CalledProcessError as e:
        print("Not FOUND in SSDlist", fileName)
        return False
    print("FOUND in SSDlist", fileName)
    return True

######################################################################
def createRandomSource(param, work, rndSq, rndDq, precTsrcConfigId):
    """Set up commands for creating the random source"""

    (prec, tsrc, suffix, cfg) = precTsrcConfigId

    ensemble = param['ensemble']
    dim = ensemble['dim']
    rwNcolor = param['randomW']['rwNcolor']
    # Set normalization to match point source with three colors
    # Divide by 8 for corner subset.
    rwNorm = (rwNcolor/3.0)*dim[0]*dim[1]*dim[2]/8.0
    rwSubset = 'corner'
    rwLabel = 'RW'
    scaleFactor = None
    rwParams = [rwNcolor, rwNorm, rwSubset, scaleFactor, rwLabel]

    fileCmd = param['fileCmd']

    # Table of source objects for each source key
    sources = dict()

    # Maintain SSDList to track what should be there
    jobid = param['job']['id']
    path = rndSq.path()

    # If we already have the random source, we don't generate it
    if rndSq.exist() or checkSSDList(path, jobid):
        return (sources, rwParams)

    # First create the zero-momentum random_wall source
    rwMom = [0, 0, 0]
    save = (fileCmd['src']['save'], rndSq.path())
    src = RandomColorWallSource(tsrc, rwNcolor, "KS", rwSubset, rwMom, scaleFactor, rwLabel, save )
    rwSrcDum = work.addBaseSource(src)

    # Next create reloaded random wall source for zero momentum
    loadRnd = (fileCmd['src']['load'], rndSq.path())
    saveRnd = ('forget_source',)
#    saveRnd = ('save_serial_scidac_ks_source', rndSq.pathremote())
    src = VectorFieldSource(loadRnd, [0,0,0,tsrc], rwNcolor, "KS", rwSubset, 
                            rwMom, scaleFactor, rwLabel, saveRnd )
    sources[makeSrcKey(('d',makeMomKey(rwMom)))] = work.addBaseSource(src)
    
    # Record file that should go on the SSD
    if param['scriptMode'] != 'KSscan':
        updateSSDList(path, jobid)
    
    # Do dummy propagator
    # Any quark will do here
    quark = param['quarks']['qlight']
    mass = 1.0
    naik_epsilon = quark['naik_epsilon'][0]
    twist = [ 0, 0, 0 ]
    load = ('fresh_ksprop',)
    save = ('forget_ksprop',)
    
    maxCG = quark['maxCG']
    check = 'sourceonly'
    precision = 1
    thisSet = KSsolveSet(rwSrcDum, twist, check, maxCG, precision)
    deflate = None
    if param['eigen']['Nvecs'] > 0:
        deflate = 'no'
    if prec == 'L':
        residual = quark['residual_loose']
    else:
        residual = quark['residual_fine']
    thisQ = KSsolveElement(mass, naik_epsilon, load, save, deflate, residual)
    thisSet.addPropagator(thisQ)
    work.addPropSet(thisSet)
    
    return (sources, rwParams)


######################################################################
def makeBaseSource(work, sources, srcKeyBase, rwParams, fileCmd, rndSq, tsrc):
    """Generate the base source if not already done"""

    (smSrc, momKey) = splitSrcKey(srcKeyBase)
    (rwNcolor, rwNorm, rwSubset, scaleFactor, rwLabel) = rwParams
    try:
        ptSrc = sources[srcKeyBase]
    except KeyError:
        load = (fileCmd['src']['load'], rndSq.path())
        save =('forget_source',)
        rwMom = splitMomKey(momKey)
        src = VectorFieldSource(load, [0,0,0,tsrc], rwNcolor, "KS", rwSubset, rwMom, scaleFactor, rwLabel, save )
        ptSrc = sources[srcKeyBase] = work.addBaseSource(src)

    return ptSrc

######################################################################
def makeModifiedSource(param, work, sources, ptSrc, srcKeyMod, fileCmd, wf1S):
    """Generate a modified source if needed"""

    ensemble = param['ensemble']

    (smSrc, momKey) = splitSrcKey(srcKeyMod)

    # Provision for a source rotation that must correlate with the quark propagator
    try:
        (smSrc, q) = smSrc.split(":")
    except ValueError:
        pass
    
    # Smear as a modified source if requested
    try:
        thisSrc = sources[srcKeyMod]
    except KeyError:
        if smSrc == '1S':
            load = (fileCmd['wf']['load'], wf1S.path())
            save = ('forget_source',)
            afm = ensemble['atrue']
            stride = param['KSaction']['stride']
            label = smSrc
            src = RadialWavefunction(label, afm, stride, load, save, ptSrc )
            thisSrc = sources[srcKeyMod] = work.addModSource(src)
        elif smSrc == 'rot':
            save = ('forget_source',)
            d1 = param['quarks'][q]['d1']
            label = smSrc
            src = FermilabRotation(label, d1, save, ptSrc )
            thisSrc = sources[srcKeyMod] = work.addModSource(src)
        else:
            print("ERROR. Unexpected source key", smSrc, "in", srcKeyMod)
            sys.exit(1)

    return thisSrc


######################################################################
def startKSSolveSet(param, qk, prec, thisSrc):
    """Start the KS solve set"""

    quark = param['quarks'][qk]
    maxCG = quark['maxCG']
    check = 'yes'
    twist = [0, 0, 0]
    if prec == 'L':
        precision = quark['precision']
    else:
        precision = 2

    thisSet = KSsolveSet(thisSrc, twist, check, maxCG, precision)

    return thisSet

######################################################################
def solveKSProp(param, work, thisSet, propFiles, quarks, quarkKeys, 
                qk, mass, naik, qkKeyBase, thisSrc, precTsrcConfigId):
    """ks_spectrum version: Compute a KS propagator"""

    # If we already have the base propagator, use it.
    if qkKeyBase in quarks.keys():
        return quarks[qkKeyBase]

    # Otherwise, set up the calculation of the basic propagator
    (prec, tsrc, suffix, cfg) = precTsrcConfigId

    ensemble = param['ensemble']
    run = ensemble['run']

    root = param['files']['root']
    projectRoot = root['project']
    localRoot = root['local']

    fileCmd = param['fileCmd']

    quark = param['quarks'][qk]
    twist = [ 0, 0, 0 ]
    qkType = quark['type']
    check = 'yes'
    
    # If we already have this propagator in a file, load it.
    # Otherwise, start from zero
    prop = param['files']['prop']
    name = propNameKS(qkKeyBase, run, precTsrcConfigId)

    # Store propagators in subdirectories labeled by the configuration ID
    configId = codeCfg(suffix, cfg)
    remotePath = prop['subdirs'] + [configId]
    propFiles[qkKeyBase] = StageFile(localRoot, None, root[prop['root']], 
                                     remotePath, name, 'r', None, None, False)
    # Record file that should go on the SSD
    jobid = param['job']['id']
    path = propFiles[qkKeyBase].path()
    if propFiles[qkKeyBase].exist() or checkSSDList(path, jobid):
        load = (fileCmd['propKS']['load'],propFiles[qkKeyBase].path())
        save = ('forget_ksprop',)
#        save = (fileCmd['propKS']['save'], propFiles[qkKeyBase].path())
    else:
        load = ('fresh_ksprop',)
        save = (fileCmd['propKS']['save'], propFiles[qkKeyBase].path())
        # Record file that should go on the SSD
        if param['scriptMode'] != 'KSscan':
            updateSSDList(propFiles[qkKeyBase].path(), param['job']['id'])
    
    deflate = None
    if param['eigen']['Nvecs'] > 0:
        deflate = quark['deflate'] 
    if prec == 'L':
        residual = quark['residual_loose']
    else:
        residual = quark['residual_fine']
    thisQ = KSsolveElement(mass, naik, load, save, deflate, residual)
    thisSet.addPropagator( thisQ )

    # Create the "quark" as a copy of this basic propagator
    # but only if we need it explicitly later for any of the npts
    # Otherwise, any sink treatment can be done directly on the propagator
    if qkKeyBase in quarkKeys:
        save = ('forget_ksprop',)
        # Kludge to get a flattened copy.  Append ".sav" to prevent restaging the file later.
#        save = ('save_serial_scidac_ksprop', propFiles[qkKeyBase].pathremote() + '.sav')
        thisQ = quarks[qkKeyBase] = QuarkIdentitySink( thisQ, 'd', save)
        work.addQuark(thisQ)
    else:
        quarks[qkKeyBase] = thisQ

    return thisQ

######################################################################
def applySinkOp(param, work, quarks, quark, qkKeyMod, snkKeyMod, thisQ, wf1S, prec, tsrc):
    """Apply sink operator"""

    ensemble = param['ensemble']
    fileCmd = param['fileCmd']

    residQuality = prec

    try:
        (smSnk, extT, stP, qkP, mQkP, epsP) = splitSnkKey(snkKeyMod)
    except ValueError:
        (smSnk, extT, stP, qkP, mQkP, epsP) = (snkKeyMod, None, None, None, None, None)

    save = ('forget_ksprop',)
    if smSnk == '1S':
        label = smSnk
        afm = ensemble['atrue']
        stride = param['KSaction']['stride']
        load = (fileCmd['wf']['load'], wf1S.path())
        thisQ = RadialWavefunctionSink(thisQ, label, afm, stride, load, save)
    elif smSnk == 'ext':
        Bmomentum = [0, 0, 0]
        label = 'x'
        save = ['forget_ksprop', ]
        T = int(extT)
        t = ( tsrc + T ) % ensemble['dim'][3]

        # Make key for extended source
        snkKeyExt = makeSnkKey((smSnk, extT, stP, qkP))
        (prec, qk, mass, naik_epsilon, rndId, srcKeyMod, snkKeyDummy) = splitQuarkKey(qkKeyMod)
        qkKeyExt = makeQuarkKey((residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, snkKeyExt))

        # If this key is already known, don't remake it
        if qkKeyExt in quarks.keys():
            q = quarks[qkKeyExt]
        # Otherwise, make it and remember it
        else:
            qExtSrc = KSExtSrcSink(thisQ, stP, Bmomentum, t, label, save)
            q = quarks[qkKeyExt] = work.addQuark(qExtSrc)

        # Use 1S smearing for parent meson
#         afm = ensemble['atrue']
#         stride = param['KSaction']['stride']
#         smLoad = (fileCmd['wf']['load'], wf1S.path())
#         qExtSrcSmear = RadialWavefunctionSink(q, '1S', afm, stride, smLoad, save)
#         q = work.addQuark(qExtSrcSmear)

        u0 = ensemble['u0']
        twist = [ 0, 0, 0 ]
        quarkP = param['quarks'][qkP]
        deflate = quarkP['deflate'] 
        if prec == 'L':
            residual = quarkP['residual_loose']
        else:
            residual = quarkP['residual_fine']
        thisQ = KSInverseSink(q, mQkP, epsP, u0, quarkP['maxCG'], deflate, residual,
                              quarkP['precision'], twist, label, save)
    else:
        print("Unrecognized sink smearing", smSnk, "in", qkKeyMod)

    quarks[qkKeyMod] = work.addQuark(thisQ)

######################################################################
def createKSQuarks(param, work, sources, quarkKeys, rwParams, rndSq, wf1S, precTsrcConfigId):
    """For ks_spectrum code: Create staggered quark propagators for tying together to make hadrons"""

    (prec, tsrc, suffix, cfg) = precTsrcConfigId

    configId = codeCfg(suffix, cfg)
    tsrcId = codeTsrc(prec, tsrc)

    # Table of propagator files
    propFiles = dict()

    # Table of quark objects for each quark key
    quarks = dict()

    srcKeyModLast = ''

    # Run through the quark keys, sorted so multiple masses with the
    # same source appear together.  Grouping them in this way allows
    # the MILC ks_spectrum code to use the multimass inverter.
    for qkKeyMod in sorted(quarkKeys,key=cmp_to_key(cmpQuarkKeys2)):
        (residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, snkKeyMod) = splitQuarkKey(qkKeyMod)
        (smSrc, momKey) = splitSrcKey(srcKeyMod)
    
        # Call for the point source first if it is unknown
        srcKeyBase = makeSrcKey(('d', momKey ))
        ptSrc = makeBaseSource(work, sources, srcKeyBase, rwParams, param['fileCmd'], rndSq, tsrc)
    
        # Modified source, if needed
        thisSrc = makeModifiedSource(param, work, sources, ptSrc, srcKeyMod, param['fileCmd'], wf1S)
    
        # Compute propagator from this source if we don't already have the file
        # Start with the basic propagator without any sink treatment
        qkKeyBase = makeQuarkKey((residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, 'd'))
    
        if 1:
            # Build the solve set (multimass version)

            if srcKeyMod != srcKeyModLast:
                # When the source changes, add the previous solve set

                if len(srcKeyModLast) > 0:
                    work.addPropSet(thisSet)
                thisSet = startKSSolveSet(param, qk, residQuality, thisSrc)
                srcKeyModLast = srcKeyMod
        else:
            # Build the solve set (single-mass version)

            if len(srcKeyModLast) > 0:
                work.addPropSet(thisSet)
            thisSet = startKSSolveSet(param, qk, thisSrc)
            srcKeyModLast = srcKeyMod

        thisQ = solveKSProp(param, work, thisSet, propFiles, quarks, quarkKeys, 
                            qk, mass, naik_epsilon, qkKeyBase, thisSrc, precTsrcConfigId)

        # Do sink treatment on propagator if we don't have the result already
        if qkKeyMod not in quarks.keys():
            applySinkOp(param, work, quarks, param['quarks'][qk], qkKeyMod, snkKeyMod, thisQ, wf1S, prec, tsrc)

    # Add the last propagator set
    if len(srcKeyModLast) > 0:
        work.addPropSet(thisSet)

    return ( quarks, propFiles )

######################################################################
def createCorrelators(param, work, quarks, correlators, rwParams, fileCmd, prec, tsrc):
    """Tie quark propagators together to create npts"""

    (rwNcolor, rwNorm, rwSubset, scaleFactor, rwLabel) = rwParams
    for corr in correlators:
        (corrFile, QKey, aQKey, mom, corrAttrs) = corr
        om = oppMom(mom)
        pmom = "p{0:d}{1:d}{2:d}".format(*tuple(mom))
        if prec == 'L':
            postfix = "-".join([pmom,'loose'])
        else:
            postfix = "-".join([pmom,'fine'])
            
        # The corrAttrs apply to only one momentum
        npts = list()
        for corrAttr in corrAttrs:
            (prefix, phase, stSnk) = corrAttr
            npts.append( MesonNpt(prefix, postfix, (phase,'/',rwNorm), [stSnk], om, ('EO','EO','EO')) )
    
        # Generate the pair stanzas
        rOffset = [0,0,0,tsrc]
        spectSave = ( fileCmd['corr']['save'], corrFile.path() )
        spect = MesonSpectrum(quarks[aQKey], quarks[QKey], rOffset, npts, spectSave)

        if param['scriptMode'] != 'KSscan':
            work.addMeson(spect)

######################################################################
def defineTarFile(param, seriesCfg):
    """Define the tar file for this cfg and step"""

    configId = decodeSeriesCfg(seriesCfg)

    tar = setUpJobTarFile(param, configId)

    return tar
    
######################################################################
def collectKSProps(param, quarkKeys):
    """Add to the list of needed light quark propagators"""

    for qkKeyMod in sorted(quarkKeys,key=cmp_to_key(cmpQuarkKeys)):
        (residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, snkKeyMod) = splitQuarkKey(qkKeyMod)
        if param['quarks'][qk]['type'] == 'KS':
            (smSrc, momKey) = splitSrcKey(srcKeyMod)
            hisqProps = param['hisqProps']
            appendUnique(hisqProps, [smSrc, rndId, momKey, mass, naik_epsilon, qk] )

######################################################################
#def rebuildKSQuarkKeys(param, quarkKeys):
#    """Reconstruct list of KS quark keys from light propagator list"""
#
#    residQuality = param['residQuality']
#    hisqProps = param['hisqProps']
#    for hisqProp in hisqProps:
#        (smSrc, rndId, momKey, mass, naik_epsilon, qk) = hisqProp
#        srcKeyMod = makeSrcKey([smSrc, momKey])
#        # For generating KS propagators, we choose only a point sink 'd'
#        qkKeyMod = makeQuarkKey([residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, 'd'])
#        appendUnique(quarkKeys, qkKeyMod)

######################################################################
def createMILCprompts(param, nstep, precTsrcConfigId, precTsrcConfigIdSym, kjob, njobs):
    """Create MILC prompts based on YAML file.  Do this for this cfg, prec, tsrc, and nstep"""

    (prec, tsrc, suffix, cfg) = precTsrcConfigId

    # Construct job stdio, stdout, stderr, log file
    (stdin, stdout, stderr, stdlog) = setUpJobIOFiles(param, nstep, precTsrcConfigId,
                                                      precTsrcConfigIdSym, kjob, njobs )
    
    # Stage lattice file
    (latCoul, loadLat, saveLat, gFix) = stageLattice(param, suffix, cfg)

    # Stage eigenpair file
    (eigenPair, loadEigen, saveEigen) = stageEigen(param, suffix, cfg)
    
    # Fetch 1S wavefunction file
    wf1S = fetchWF(param)
    
    # SSDlist
    createSSDList(param['job']['id'])
    
    # Random source
    (rndSq, rndDq, rndQ, rndAq) = prepareRandomSource(param, precTsrcConfigId)
    
    # Start input parameter set.  Prompt information is accumulated in "work".
    work = initializePrompts(param, precTsrcConfigId)

    # Construct tables of propagators to be generated and correlators
    # to be computed
    quarkKeys = list()   # List of propagaator attributes including extended props
#    if param['scriptMode'] == 'KSproduction':
#        rebuildKSQuarkKeys(param, quarkKeys)

    correlators = list() # List of hadron npt correlators
    compile2ptCorrelators( param, correlators, quarkKeys, rndQ, rndAq, nstep, precTsrcConfigId)
    compile3ptCorrelators( param, correlators, quarkKeys, rndQ, rndAq, nstep, precTsrcConfigId)

    # Append to list of needed HISQ quark propagators to param['hisqProps']
    if param['scriptMode'] == 'KSscan':
        collectKSProps(param, quarkKeys)
        if False:
            for qK in quarkKeys:
                print(qK)

    # Add gauge load and gauge-fix stanzas
    startGauge(param, work, loadLat, saveLat, gFix)

    # Add eigenpair specification
    addEigen(param, work, loadEigen, saveEigen)

    # Generate commands for creating the random sources
    (sources, rwParams) = createRandomSource(param, work, rndSq, rndDq, 
                                             precTsrcConfigId)
    
    # Construct quark propagators (including extended ones) from the quark key list
    (quarks, propFiles) = createKSQuarks(param, work, sources, quarkKeys, 
                                         rwParams, rndSq, wf1S, precTsrcConfigId)
    
    # Create correlators
    createCorrelators(param, work, quarks, correlators, rwParams, param['fileCmd'], prec, tsrc)
    
    # Write the MILC prompts
    if param['scriptMode'] != 'KSscan':
        work.generate(stdin.openwrite())
        stdin.close()

    asciiIOFiles = (stdin, stdout, stderr, stdlog)
    binIOFiles = (latCoul, rndSq, rndDq, propFiles)

    return asciiIOFiles, binIOFiles

############################################################
def launchJob(param, asciiIOFileSet, njobs):
    """Launch the job"""

    (stdin, stdout, stderr, stdlog) = asciiIOFileSet

    # Get locale for job launching
    locale = param['submit']['locale']
    try:
        launchParam = param['launch'][locale]
    except KeyError:
        print("ERROR: Launch parameters for locale", locale, "not defined in the YAML parameter file.")
        sys.exit(1)

    # Job launch executable
    mpirun = launchParam['mpirun']
    # Parameters for job launch executable
    layout = param['submit']['layout']
    mpiparam = launchParam['mpiparam']
    # Replace "NP" with the requested number of MPI ranks in mpiparam line
    np = layout['basenodes'] * layout['ppn'] * njobs
    mpiparam = re.sub('NP', str(np), mpiparam)
    try:
        mpiparam = re.sub('MYHOSTFILE', os.environ['MYHOSTFILE'], mpiparam)
    except KeyError:
        pass
    # Numa control
    numa = launchParam['numa']
    # Optional launch script (needed for Summit)
    try:
        launchScript = launchParam['launchScript']
    except KeyError:
        launchScript = ''
    # Executable
    bin = param['files']['exec']
    name = bin['name']
    root = param['files']['root']
    # We don't stage the executable on the localRoot directory because it must be
    # visible to all nodes
    binFile = StageFile( None, None, root[bin['root']], bin['subdirs'], 
                         name, 'r', None, None, False)
    execFile = binFile.path()
    # qmp parameters
    qmpgeom = " -qmp-geom {0:d} {1:d} {2:d} {3:d}".format(*tuple(param['submit']['layout']['layoutSciDAC']['node']))
    # Multijob parameters
    if njobs > 1:
        qmpjob = " -qmp-job {0:d} {1:d} {2:d} {3:d}".format(*tuple(param['submit']['layout']['jobGeom']))
    else:
        qmpjob = ""
    # stdio
    inFile = stdin.path()
    outFile = stdout.path()
    errFile = stderr.path()
    # Complete command
    cmd = ' '.join([ mpirun, mpiparam, numa, launchScript, execFile, qmpgeom, qmpjob, inFile, outFile, errFile ])
    print("#", cmd)
    sys.stdout.flush()

    # Launch the job.  But if debugging, just print the command
    if param['scriptDebug'] == 'debug':
        fp = open(param['jobcmdfile'],'a')
        print(cmd,file=fp)
        fp.close()
        return
    else:
        try:
            subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print("ERROR: ", mpirun, "exited with code", e.returncode, ".")
            return 1
    return 0
    
######################################################################
def checkComplete(param, tarFile):
    """Check that output file is complete"""

    # We check the file size
    try:
        reply = subprocess.check_output(["ls", "-l", tarFile])
    except subprocess.CalledProcessError as e:
        print("Error", e.returncode, "stat'ing output tar file", tarFile)
        return False

    # File size in bytes is the 5th field in ls -l
    tarFileSize = int(reply.split()[4])
    tarFileGood = param['tarCheck']['tarbzip2Size']
    # Allow for a 5% variation
    
    if tarFileSize*1.05 < tarFileGood:
        print("Output tar file", tarFile, "size", tarFileSize, "too small.")
        return False

    # We check the number of entries in the tar file
    try:
        reply = subprocess.check_output("tar -tjf " + tarFile + "| wc -l", shell = True)
    except subprocess.CalledProcessError as e:
        print("Error tar-listing", tarFile)
        return False
    
    # Entry count is first field
    entries = int(reply.split()[0])
    entriesGood = param['tarCheck']['tarEntries']
    
    if entries < param['tarCheck']['tarEntries']:
        print("Output tar file", tarFile, "entry count", entries, "too low.")
        return False

    # Passed these tests
    print("Output tar file is complete")

    return True

############################################################
def tarList(scriptDebug, tarbase, dirs, suffix, cfg):
    """Construct a list of files for including in the tar ball"""
    # Lists all files in the dirs ending with the specified suffix and cfg number
    
    configId = codeCfg(suffix, cfg)
    # Name of the tar-list file
    tList = "tar." + configId
    tListPath = tarbase + "/" + tList
    # First delete any stale tar-list file
    cmd = ['/bin/rm -f', tListPath]
    cmd = ' '.join(cmd)
    if scriptDebug != 'debug':
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
        if scriptDebug != 'debug':
            try:
                lines = subprocess.check_output(cmd, shell = True).splitlines()
            except subprocess.CalledProcessError as e:
                print("Error finding files in", tarbase, d)
    return tListPath
    
############################################################
def storeFiles(param, asciiFileList, binFileList):
    """Copy result files to the archive and clean up"""

    # Copy the output lattice, random sources, and propagators to the remote directory
    (stdin, stdout, stderr, stdlog) = asciiFileList
    (latCoul, rndSq, rndDq, propFiles) = binFileList
    latCoul.store()
    rndSq.store()
    rndDq.store()
    for p in propFiles.keys():
        propFiles[p].store()

    # Copy system stdout to log file
#    jobID = param['job']['id']
#    cmd = ['/bin/cp', jobID + ".output", stdlog.path()]
#    cmd = ' '.join(cmd)
#    print("#", cmd)
#    if param['scriptDebug'] != 'debug':
#        try:
#            subprocess.check_output(cmd, shell = True)
#        except subprocess.CalledProcessError as e:
#            print("WARNING: /bin/cp failed for", e.cmd)

    # Resolve multijob names and clean up
    stdin.store()
    stdout.store()
    stderr.store()
    stdlog.store()

############################################################
def storeTarFile(param, seriesCfg, tar):
    """Create and copy tar file to the archive and clean up"""

    suffix, cfg = decodeSeriesCfgSrc(seriesCfg)

    # Create tarball and store it
    tarbase = tar.dirLocal()
    if tarbase == None:
        tarbase = tar.dirRemote()
    tardirs = param['files']['tar']['list']

    if 0:
        # Get a list of paths in the directories tardirs with matching configuration number
        tListPath = tarList( param['scriptDebug'], tarbase, tardirs, suffix, cfg )

        # Create the tarball and check it for completeness
        cmd = ['/bin/tar', '-C', tarbase, '--remove-files', '-cjf', tar.path(), '-T', tListPath]
        cmd = ' '.join(cmd)
        print("#", cmd)
        if param['scriptDebug'] != 'debug':
            subprocess.check_output(cmd, shell = True)
            if checkComplete(param, tar.path()):
                tar.store()
            else:
                tar.store()
                print("WARNING:", tar.path(), "INCOMPLETE.")

############################################################
def purgeProps(binFileList):
    """TEMPORARY: delete staged propagator files to make room on /scratch"""
    (latCoul, rndSq, rndDq, propFiles) = binFileList
    for p in propFiles.keys():
        propFiles[p].delete_staged()
    
############################################################
def doJobSteps(param, tsrcs, precs, njobs, seriesCfgsrep, asciiIOFileSets, 
               binIOFileSets):
    """Do the job steps for the given source times"""

    # FOR TSM TUNING ONLY!!
    # tsrcs = [ 0 ] * njobs

    # Job steps for all cfgs in this group
    steprange = param['job']['steprange']
    for nstep in range(steprange['low'], steprange['high']):

        print(datetime.now(),"Processing", param['scriptMode'], seriesCfgsrep,
              "for step", nstep, "tsrc", tsrcs)

        # Create MILC prompts and filenames for all cfgs in
        # this group for these tsrcs and all steps
        # For multijob, the base path and file name derives from the first subjob in the set
        # The full paths include a suffix ".jnn" where nn = kjob is the subjob index
        # These multijob paths are symlinks to the actual files
        # If njobs = 1, no symlinks are created
        (suffixSym, cfgSym) = decodeSeriesCfg(seriesCfgsrep[0])
        precSym = precs[0]
        tsrcSym = tsrcs[0]
        precTsrcConfigIdSym = (precSym, tsrcSym, suffixSym, int(cfgSym))
        for kjob in range(njobs):
            print(datetime.now(),"Creating MILCprompts for job",kjob)
            seriesCfg = seriesCfgsrep[kjob]
            (suffix, cfg) = decodeSeriesCfg(seriesCfg)
            prec = precs[kjob]
            tsrc = tsrcs[kjob]
            precTsrcConfigId = (prec, tsrc, suffix, int(cfg))
            a, b = createMILCprompts(param, nstep, precTsrcConfigId,
                                     precTsrcConfigIdSym, kjob, njobs)
            # Key for this configuration and source time
            seriesCfgPrecSrc = encodeSeriesCfgPrecSrc(seriesCfg,precs[kjob],str(tsrcs[kjob]))
            asciiIOFileSets[seriesCfgPrecSrc] = a
            binIOFileSets[seriesCfgPrecSrc] = b

        # Launch the job for this group (unless we are just scanning)
        # For multijob compatibility, use the first entry in the list for stdin, stdout, stderr
        if param['scriptMode'] != 'KSscan':
            print(datetime.now(),"Launching set", seriesCfgsrep, "for step", nstep,
                  "tsrcs", tsrcs, "precs", precs)
            seriesCfgPrecSrc = encodeSeriesCfgPrecSrc(seriesCfgsrep[0],precs[0],str(tsrcs[0]))
            status = launchJob(param, asciiIOFileSets[seriesCfgPrecSrc], njobs)

            # List files created
            if param['files']['root']['local'] != None:
                cmd = ' '.join(['ls', '-l',  param['files']['root']['local']+'/*'])
                try:
                    subprocess.check_output(cmd, shell=True)
                except subprocess.CalledProcessError as e:
                    print("Error listing files.  Return code", e.returncode)

#           We will take care of cleanup afterwards                    
            # Resolve symlinks and store all result files, propagators, sources, etc.
#            for seriesCfgPrecSrc in sorted(asciiIOFileSets.keys()):
#                series, cfg, tsrca, prec = decodeSeriesCfgPrecSrc(seriesCfgPrecSrc)
#                print(datetime.now(),"Storing files for", series, cfg)
#                storeFiles(param, asciiIOFileSets[seriesCfgPrecSrc], binIOFileSets[seriesCfgPrecSrc])
#                purgeProps(binIOFileSets[seriesCfgPrecSrc])  # TEMPORARY
            
            if status == 1:
                print("Quitting due to errors")
                sys.exit(1)

############################################################
def runParam(seriesCfgs, precTsrcs, ncases, njobs, param):
    """Run with the given parameter set"""

    # Configurations are processed in groups of njob independent parallel computations (multijob)
    # There are nreps such groups in a job.  Usually we have ncases = njobs, so nreps = 1.
    nreps = ncases // njobs

    # Run through groups of configurations
    for irep in range(nreps):

        asciiIOFileSets = dict()
        binIOFileSets = dict()
        tarFileSets = dict()

        # List of cfgs to process in parallel (multijob) in this group
        seriesCfgsrep = seriesCfgs[irep*njobs:(irep+1)*njobs]
        precTsrcsrep = precTsrcs[irep*njobs:(irep+1)*njobs]

# We decided not to generate tar files on the compute nodes
#        # Create the tarfiles for all cfgs in this group
#        for seriesCfg in seriesCfgsrep:
#            tarFileSets[seriesCfg] = defineTarFile(param, seriesCfg)

        precs = []
        tsrcs = []
        for kjob in range(njobs):
            prec, tsrc = decodePrecTsrc(precTsrcsrep[kjob])
            precs.append(prec)
            tsrcs.append(int(tsrc))

        print(datetime.now(),"Calculation with tsrcs", tsrcs, "and precs", precs)
        sys.stdout.flush()
        doJobSteps(param, tsrcs, precs, njobs, seriesCfgsrep, asciiIOFileSets, binIOFileSets)

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
def initParam(param, myjobid):
    """Set some initial values of params"""

    # Add the remote and archive roots to the yaml-generated dictionary:
    addRootPaths(param)

    # Add my job ID
    param['myjobid'] = myjobid

    # Assume that we are debugging if we are not on PBS
    param['scriptDebug'] = 'KSproduction'
    job = param['job']
    locale = param['submit']['locale']
    launchParam = param['launch'][locale]
    try:
        # Get the job ID number from the batch system
        # Used to make a unique label for the job files
        # Works at least for PBS_JOBID and SLURM_JOBID
        # PBS_JOBID: 805642.pi0s.fnal
        # SLURM_JOBID: 2003326
        # New global "id" added to "job" stanza
        job['id'] = os.environ[launchParam['jobidName']].split(".").pop(0)
    except KeyError:
        job['id'] = param['myjobid']
        param['scriptDebug'] = 'debug'
        print("WARNING: JOBID not found.  Changed to debug mode. Will not launch job.")


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
def loadParams(YAMLAll, YAMLLaunch, YAMLEns, YAMLMachine, myjobid):
    """Load a set of YAML parameter files into a single dictionary"""

    # Initial parameter file
    param = loadParamsJoin(YAMLEns, YAMLAll)
        
    # Load parameters defining the launch environment for various locales
    paramLaunch = loadParam(YAMLLaunch)
    param = updateParam(param, paramLaunch)

    # Load parameters specific to the machine and installation
    paramMachine = loadParam(YAMLMachine)
    param = updateParam(param, paramMachine)

    # Add further initial values to the parameters
    initParam(param, myjobid)

    return param

############################################################
def main():

    # Set permissions
    os.system("umask 022")

    # Command-line args:
    if len(sys.argv) < 10:
        print("Usage", sys.argv[0], "<cfgList> <tsrcList> <ncases> <njobs> <myjobid> <jobcmdfile> <yaml> <yaml-launch> <yaml-ens> <yaml-machine>")
        sys.exit(1)

    # Decode arguments 
    # cfgList     List of ncases configuration numbers to run.  Format a.102/a.102/a.108/...
    # tsrcList    List of ncases source times to run (includes precision label) Format L.0/L.12/L.0/...
    # ncases      Number of cases to process in this job
    # njobs       Number of simultaneous subjobs to run
    # myjobid     A unique label for the job
    # jobcmdfile  Where we write the job launch commands
    # YAML        Basic parameter file in yaml format                    
    # YAMLLaunch  Job launching information in yaml format                    
    # YAMLEns     Ensemble parameter file in yaml format                    
    # YAMLMachine Machine/installation parameter file in yaml format                    

    (cfgList, tsrcList, ncases, njobs, myjobid, jobcmdfile, YAML, YAMLLaunch, YAMLEns, YAMLMachine) = sys.argv[1:11]

    print("Have args", cfgList, tsrcList, ncases, njobs, myjobid, jobcmdfile, YAML, YAMLLaunch, YAMLEns, YAMLMachine)

    seriesCfgs = cfgList.split("/")    
    precTsrcs = tsrcList.split("/")
    ncases = int(ncases)
    njobs = int(njobs)         

    if len(seriesCfgs) != ncases or len(precTsrcs) != ncases:
        print("ERROR: Number of cases", ncases, "is not equal to the number of lattices or source times")
        sys.exit(1)

    if ncases % njobs != 0:
        print("ERROR: Number of cases", ncases, "must be divisible by the number of jobs", njobs)
        sys.exit(1)

    # Load the basic parameter set
    param = loadParams(YAML, YAMLLaunch, YAMLEns, YAMLMachine, myjobid)

    # We generate the non-extended staggered propagators first.  So we
    # need to collect a shopping list of propagators.  The list is
    # created by scanning the heavylight 2pt and 3pt correlators and
    # listing what is needed.  The shopping list is put in hisqProps.
    param['scriptMode'] = 'KSscan'
    param['hisqProps'] = list()

    print("Scanning with the parameter set", YAML)
    sys.stdout.flush()
    runParam(seriesCfgs, precTsrcs, ncases, njobs, param)

    # Dump the collected propagator list
    hisqProps = param['hisqProps']
    for hisqProp in sorted(hisqProps):
        print(hisqProp)
        
    print("#############################################")
        
    # Now generate the hisq staggered propagators, two-points,
    # and three-points based on the shopping list "hisqProps"

    # Restore the initial parameter set
    param = loadParams(YAML, YAMLLaunch, YAMLEns, YAMLMachine, myjobid)

    # Switch from KSscan to KSproduction mode
    param['scriptMode'] = 'KSproduction'

    # Add the shopping list
    param['hisqProps'] = hisqProps

    # Name of the file that will contain the job launch commands
    param['jobcmdfile'] = jobcmdfile

    print("Running with the parameter set", YAML)
    sys.stdout.flush()
    runParam(seriesCfgs, precTsrcs, ncases, njobs, param)

    sys.exit(0)
    
############################################################
main()
