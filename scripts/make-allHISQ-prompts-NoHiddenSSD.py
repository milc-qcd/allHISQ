#! /usr/bin/env python

# Python 3 version

import sys, os, yaml, re, subprocess
sys.path.append("/Users/wijay/GitHub/MILC/milc_qcd/python3lib/MILCprompts/")
from MILCprompts import *
from allHISQKeys import *
from allHISQFilesNoHiddenSSD import *
from Cheetah.Template import Template

from datetime import datetime
from collections import namedtuple
import numpy as np
import itertools
######################################################################
# The function createMILCprompts(...) below employs a large list of
# correlators, i.e., tuples which encode the information about the quarks
# necessary to build the desired correlation function.
# For 2pt functions, we conventionally insert momentum along the "quark" line.
# For 3pt functions, we also generally insert momentum along the "quark" line,
# which corresponds to the daugther quark in the decay.
# The antiquark line corresponds to the extended propagator of the spectator
# and parent quark.
# For more general momentum configurations, it is also desirable to insert
# momentum at the source of the extended propagator.
Correlator = namedtuple(
    'Correlator',
    ['corrFile', 'quark_key', 'antiquark_key','momentum_quark', 'momentum_antiquark', 'atrributes'])

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
def encodeSeriesCfgSrc(seriesCfg,tsrc):
    """Encode series, cfg and tsrc"""
    series, cfg = decodeSeriesCfg(seriesCfg)
    return ".".join([series, cfg, tsrc])

#######################################################################
def decodeSeriesCfgSrc(seriesCfgSrc):
    """Decode series, cfg, and tsrc"""
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
                         lat['subdirs'], name, 'r', None, False )
    inLat = latCoul
    loadLat = (fileCmd['lat']['load'], inLat.path())
    saveLat = ('forget',)
    gFix = 'no_gauge_fix'

    if not latCoul.exist():
        name = latFileMILCv5( run, suffix, cfg)
        lat = param['files']['latMILCv5']
        latMILCv5 = StageFile( localRoot, None, root[lat['root']],
                               lat['subdirs'], name, 'r', None, False )
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
                         name, 'r', None, False )

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
                      name, 'r', None, False )
    if not wf1S.exist():
        if param['scriptDebug'] != 'debug':
            print("ERROR: Can't get wavefunction file.")
            sys.exit(1)
    return wf1S

######################################################################
def prepareRandomSource(param, tsrcConfigId):
    """Fetch or prepare to generate the random wall source"""

    (tsrc, suffix, cfg) = tsrcConfigId

    # Random source files for spectator and daughter
    root = param['files']['root']
    localRoot = root['local']

    ensemble = param['ensemble']
    run = ensemble['run']

    rand = param['files']['rand']
    if rand['coherent'] == 'yes':
        # Files must exist
        name = rndFile('', run, tsrcConfigId)
        rndDq = StageFile( localRoot, None, root[rand['root']], rand['subdirs'],
                           name, 'r', None, False )
        name = rndFile('Sq', run, tsrcConfigId)
        rndSq = StageFile( localRoot, None, root[rand['root']], rand['subdirs'],
                           name, 'r', None, False )
        if not rndDq.exist() or not rndSq.exist():
            print("ERROR: with coherent random sources",rndDq.name(),"and",rndSq.name(),"must exist")
            if param['scriptDebug'] != 'debug':
                sys.exit(1)
    else:
        name = rndFile('', run, tsrcConfigId)
        # Store random sources in subdirectories labeled by the configuration ID
        configID = codeCfg(suffix, cfg)
        remotePath = rand['subdirs'] + [configID]

#        rndDq = StageFile( localRoot, None, root[rand['root']], rand['subdirs'], name, 'x', None, False )
#        rndSq = StageFile( localRoot, None, root[rand['root']], rand['subdirs'], name, 'x', None, False )
        rndDq = StageFile( localRoot, None, root[rand['root']], remotePath,
                           name, 'r', None, False )
        rndSq = StageFile( localRoot, None, root[rand['root']], remotePath,
                           name, 'r', None, False )

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
def compile2ptCorrelators(param, correlators, quarkKeys, rndQ, rndAq, nstep, tsrcConfigId):
    """Parse the YAML 2pt parameters and make tables of propagators to
    be generated and 2pt correlators to be computed"""
    def unpack(quark_specification):
        """
        Unpackage the YAML specification of a quark or antiquark.
        The relevant YAML typically have the form
            Q: [ 'qlight', ['d'], ['d'] ].
        or
            Q: [ 'qlight', ['d'], ['d'], <specification of twist> ].
        Usage:
        corr2pts = param['corr2pts']
        (qk, smQSrcList, smQSnkList, qTwist) = corr2pts[nptKey]['Q']
        (aQk, smAQSrcList, smAQSnkList, aQTwist) = corr2pts[nptKey]['aQ']
        """
        if len(quark_specification) == 3:
            (qk, smQSrcList, smQSnkList) = quark_specification
            twistKey = None
        elif len(quark_specification) == 4:
            (qk, smQSrcList, smQSnkList, twist) = quark_specification
            twistKey = makeTwistKey(twist)
        else:
            raise ValueError(f"Unrecognized YAML structure for corr2pts[{nptKey}]")
        return qk, smQSrcList, smQSnkList, twistKey

    def assemble_tokens(residQuality, qk, m, eps, rnd, smSrc, smSnk, mom, twist):
        """
        Line up the 'tokens' necessary to build a quark key
        """
        srcKey = makeSrcKey((smSrc, makeMomKey(mom)))
        if twist:
            tokens = (residQuality, qk, m, eps, rnd, srcKey, smSnk, twist)
        else:
            tokens = (residQuality, qk, m, eps, rnd, srcKey, smSnk)
        return tokens

    (tsrc, suffix, cfg) = tsrcConfigId

    root = param['files']['root']
    localRoot = root['local']
    residQuality = param['residQuality']

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

        # Quark carries the momentum and is possibly twisted
        # Make a table of quark keys encoding the needed quark attributes
        # (qk, smQSrcList, smQSnkList) = corr2pts[nptKey]['Q']
        (qk, smQSrcList, smQSnkList, qTwist) = unpack(corr2pts[nptKey]['Q'])
        for smQSrc in smQSrcList:
            for smQSnk in smQSnkList:
                for (p, stSnk, mom) in corr2pts[nptKey]['correlators']:
                    quark = param['quarks'][qk]
                    for m, eps in zip(quark['mass'], quark['naik_epsilon']):
                        tokens = assemble_tokens(residQuality, qk, m, eps, rndQ, smQSrc, smQSnk, mom, qTwist)
                        qKey = makeQuarkKey(tokens)
                        appendUnique(quarkKeys, qKey)

        # Antiquark always zero momentum and zero twist
        # Make a table of antiquark keys encoding the needed quark attributes
        # (aQk, smAQSrcList, smAQSnkList) = corr2pts[nptKey]['aQ']
        (aQk, smAQSrcList, smAQSnkList, _) = unpack(corr2pts[nptKey]['aQ'])
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
        name = corr2ptFileName(nptKey, run, tsrcConfigId)
        corr = param['files']['corr']
        (qk, smQSrcList, smQSnkList, qTwist) = unpack(corr2pts[nptKey]['Q'])
        (aQk, smAQSrcList, smAQSnkList, _) = unpack(corr2pts[nptKey]['aQ'])
        for smAQSrc in smAQSrcList:
            for smQSrc in smQSrcList:
                for smQSnk in smQSnkList:
                    for smAQSnk in smAQSnkList:
                        quark = param['quarks'][aQk]
                        for mAq, epsAq in zip(quark['mass'], quark['naik_epsilon']):
                            aQmom = [0, 0, 0]  # Hard-coded to zero. Momentum is always inserted on quark line
                            aQKey = makeQuarkKey((residQuality, aQk, mAq, epsAq, rndAq,
                                                    makeSrcKey((smAQSrc, makeMomKey(aQmom))), smAQSnk))
                            for momKey in corrAttrsTable.keys():
                                quark = param['quarks'][qk]
                                for mQ, epsQ in zip(quark['mass'], quark['naik_epsilon']):
                                    Qmom = splitMomKey(momKey)
                                    tokens = assemble_tokens(residQuality, qk, mQ, epsQ, rndQ, smQSrc, smQSnk, Qmom, qTwist)
                                    qKey = makeQuarkKey(tokens)
                                    mQkLab = massLabel(param['quarks'][qk], mQ)
                                    mAQkLab = massLabel(param['quarks'][aQk], mAq)
                                    massMomDir = massSubdir2pt(mQkLab, mAQkLab, Qmom)
                                    subDirs = [stream, corr['subdir'], residQuality, nptKey, massMomDir]
                                    corrFile = StageFile(localRoot, subDirs, root[corr['root']],
                                                            subDirs, name, 'w', None, False)
                                    correlators.append(
                                        Correlator(corrFile, qKey, aQKey, Qmom, aQmom, corrAttrsTable[momKey]))


######################################################################
def compile3ptCorrelators(param, correlators, quarkKeys, rndQ, rndAq, nstep, tsrcConfigId):
    """Parse the YAML 3pt parameters and make tables of propagators to
    be generated and 3pt correlators to be computed"""

    def unpack_daughter(quark_specification):
        """
        corr3pts[nptKey]['Dq']
        """
        if len(quark_specification) == 2:
            (qk, smDSrcList) = quark_specification
            twistKey = None
        elif len(quark_specification) == 3:
            (qk, smDSrcList, qTwist) = quark_specification
            twistKey = makeTwistKey(qTwist)
        else:
            raise ValueError("complain!")
        return (qk, smDSrcList, twistKey)

    def assemble_tokens(residQuality, qk, m, eps, rnd, smSrc, smSnk, mom, twist):
        """
        Line up the 'tokens' necessary to build a quark key
        """
        srcKey = makeSrcKey((smSrc, makeMomKey(mom)))
        if twist:
            tokens = (residQuality, qk, m, eps, rnd, srcKey, smSnk, twist)
        else:
            tokens = (residQuality, qk, m, eps, rnd, srcKey, smSnk)
        return tokens

    (tsrc, suffix, cfg) = tsrcConfigId

    root = param['files']['root']
    localRoot = root['local']

    ensemble = param['ensemble']
    run = ensemble['run']
    stream = param['stream']
    residQuality = param['residQuality']

    corr3pts = param['corr3pts']
    for nptKey in corr3pts:
        if corr3pts[nptKey]['step'] != nstep:
            continue

        # Daughter: at current (sink) not smeared and always rotated if
        # clover. Momenta are injected at daughter
        (qk, smDSrcList, qTwist) = unpack_daughter(corr3pts[nptKey]['Dq'])
        if param['quarks'][qk]['type'] == 'KS':
            smDSnk = 'd'
        else:
            smDSnk = 'rot'
        for smDSrc in smDSrcList:
            # (p, stC, mom) <--> ("phase", "spin-taste current", "momentum")
            for (p, stC, mom) in corr3pts[nptKey]['correlators']:
                quark = param['quarks'][qk]
                for m, eps in zip(quark['mass'], quark['naik_epsilon']):
                    tokens = assemble_tokens(residQuality, qk, m, eps, rndAq, smDSrc, smDSnk, mom, qTwist)
                    daughterKey = makeQuarkKey(tokens)
                    appendUnique(quarkKeys, daughterKey)

        # Parent: at current (sink) not smeared and always rotated if clover
        # Unless specified otherwise, the parent momentum defaults to zero
        qkP = corr3pts[nptKey]['Pq'][0]  # e.g., 'qheavy'
        try:
            parentMomenta = corr3pts[nptKey]['Pq'][1]  # e.g., [[1, 2, 3], [4, 5, 6]]
            for parentMom in parentMomenta:
                if len(parentMom) != 3:
                    raise ValueError(
                        "Poorly formatted momenta. Each momentum needs 3 components", parentMomenta)
        except IndexError:
            parentMomenta = [[0, 0, 0], ]

        # Spectator: extended source (sink) smearing is done
        # separately, no rotation, zero momentum at source
        (qkS, smSSrcList) = corr3pts[nptKey]['Sq']
        (qkD, smDSrcList, qTwist) = unpack_daughter(corr3pts[nptKey]['Dq'])
        smSSnk = 'ext'
        stP = corr3pts[nptKey]['spinTasteParent']
        try:
            select = corr3pts[nptKey]['select']
        except KeyError:
            select = 'all'
        for smDSrc in smDSrcList:
            for smSSrc in smSSrcList:
                for extT, parentMom in itertools.product(corr3pts[nptKey]['extT'], parentMomenta):
                    corr = param['files']['corr']
                    name = corr3ptFileName(nptKey, run, extT, tsrcConfigId)
                    quarkP = param['quarks'][qkP]
                    for mQkP, epsP in zip(quarkP['mass'], quarkP['naik_epsilon']):
                        snkKey = makeSnkKey((smSSnk, str(extT), stP, qkP, mQkP, epsP, makeMomKey(parentMom)))

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
                            specMom = [0, 0, 0]  # Spectator quark is always at rest
                            parentKey = makeQuarkKey((residQuality, qkS, mQkS, epsS, rndQ,
                                                      makeSrcKey((smSSrc, makeMomKey(specMom))), snkKey))
                            appendUnique(quarkKeys, parentKey)
                            for momKey in corrAttrsTable.keys():
                                quark = param['quarks'][qkD]
                                for mQkD, epsD in zip(quark['mass'], quark['naik_epsilon']):
                                    # Provision for doing only the diagonal mass case: skip off diagonal
                                    if select == 'diagonal' and ( mQkD != mQkP or epsD != epsP ):
                                        continue
                                    daughterMom = splitMomKey(momKey)
                                    tokens = assemble_tokens(residQuality, qkD, mQkD, epsD, rndAq, smDSrc, smDSnk, daughterMom, qTwist)
                                    daughterKey = makeQuarkKey(tokens)
                                    quark = param['quarks'][qkP]
                                    # Do we need support for multiple parent masses??
                                    mQkPLab = massLabel(param['quarks'][qkP], mQkP)
                                    mQkSLab = massLabel(param['quarks'][qkS], mQkS)
                                    mQkDLab = massLabel(param['quarks'][qkD], mQkD)
                                    massMomDir = massSubdir3pt(mQkPLab, mQkSLab, mQkDLab, daughterMom)
                                    subDirs = [stream, corr['subdir'], residQuality, nptKey, massMomDir]
                                    corrFile = StageFile(localRoot, subDirs, root[corr['root']],
                                                         subDirs, name, 'w', None, False)

                                    # correlators.append([corrFile, daughterKey, parentKey, daughterMom, corrAttrsTable[momKey]])

                                    correlators.append(
                                        Correlator(
                                            corrFile, daughterKey, parentKey,
                                            daughterMom, parentMom, corrAttrsTable[momKey]))

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
                    name, 'w', None, False)

    return tar

######################################################################
def setUpJobIOFiles(param, nstep, tsrcConfigId, tsrcConfigIdSym, kjob, njobs):
    """Define and open the stdin file, define stdout and stderr and redirect the script stdout, stderr"""

    root = param['files']['root']
    localRoot = root['local']

    ensemble = param['ensemble']
    run = ensemble['run']
    stream = param['stream']
    jobid = param['job']['id']
    residQuality = param['residQuality']

    step = 'step' + str(nstep)
    tag = ''

    io = param['files']['log']
    name = logFileName(run, tsrcConfigId, jobid, tag, step)
    multiJobName = logFileSymLink(run, tsrcConfigIdSym, jobid, tag, step, kjob, njobs)
    localpath = os.path.join( root[io['root']] )
    # Don't stage the log file.  It contains script information
    # that might be needed in case the job fails.
    subDirs = [stream, io['subdir'], residQuality]
    stdlog = StageFile(None, None, localpath, subDirs, name, 'w', multiJobName, True)
#    # Redirect script stdout and stderr to the log file
#    if param['scriptDebug'] != 'debug':
#        redirectStdoutStderr(stdlog.path())

    io = param['files']['in']
    name = inFileName(run, tsrcConfigId, jobid, tag, step)
    multiJobName = inFileSymLink(run, tsrcConfigIdSym, jobid, tag, step, kjob, njobs)
    localpath = os.path.join( root[io['root']] )
    subDirs = [stream, io['subdir'], residQuality]
    stdin = StageFile(localRoot, subDirs, localpath, subDirs, name,
                      'w', multiJobName, True)

    io = param['files']['out']
    name = outFileName(run, tsrcConfigId, jobid, tag, step)
    multiJobName = outFileSymLink(run, tsrcConfigIdSym, jobid, tag, step, kjob, njobs)
    localpath = os.path.join( root[io['root']] )
    subDirs = [stream, io['subdir'], residQuality]
    stdout = StageFile(localRoot, subDirs, localpath, subDirs, name,
                       'w', multiJobName, True)

    io = param['files']['err']
    name = errFileName(run, tsrcConfigId, jobid, tag, step)
    multiJobName = errFileSymLink(run, tsrcConfigIdSym, jobid, tag, step, kjob, njobs)
    localpath = os.path.join( root[io['root']] )
    subDirs = [stream, io['subdir'], residQuality]
    stderr = StageFile(localRoot, subDirs, localpath, subDirs, name, 'w',
                       multiJobName, True)

    return (stdin, stdout, stderr, stdlog)

######################################################################
def initializePrompts(param, tsrcConfigId):
    """Start input parameter set"""

    (tsrc, suffix, cfg) = tsrcConfigId

    ensemble = param['ensemble']
    dim = ensemble['dim']
    seed = str(cfg)+str(tsrc)
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
def createRandomSource(param, work, rndSq, rndDq, tsrcConfigId):
    """Set up commands for creating the random source"""

    (tsrc, suffix, cfg) = tsrcConfigId

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

    # If we already have the random source, we don't generate it
    if rndSq.exist():
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
    set_type = 'single'
    inv_type = 'UML'
    precision = 1
    thisSet = KSsolveSet(rwSrcDum, twist, check, set_type, inv_type, maxCG, precision)
    deflate = None
    if param['eigen']['Nvecs'] > 0:
        deflate = 'no'
    if param['residQuality'] == 'fine':
        residual = quark['residual_fine']
    else:
        residual = quark['residual_loose']
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
def startKSSolveSet(param, qk, thisSrc, twistKey=None):
    """Start the KS solve set"""

    quark = param['quarks'][qk]
    maxCG = quark['maxCG']
    check = 'yes'
    set_type = 'single'
    inv_type = 'UML'
    if twistKey is None:
        twist = [0, 0, 0]
    else:
        twist = splitTwistKey(twistKey)
    if len(twist) != 3:
        raise ValueError("Unsupported twist", twist)
    if param['residQuality'] == 'fine':
        precision = 2
    else:
        precision = quark['precision']

    thisSet = KSsolveSet(thisSrc, twist, check, set_type, inv_type, maxCG, precision)

    return thisSet

######################################################################
def solveKSProp(param, work, thisSet, propFiles, quarks, quarkKeys,
                qk, mass, naik, qkKeyBase, thisSrc, tsrcConfigId):
    """ks_spectrum version: Compute a KS propagator"""

    # If we already have the base propagator, use it.
    if qkKeyBase in quarks.keys():
        return quarks[qkKeyBase]

    # Otherwise, set up the calculation of the basic propagator
    (tsrc, suffix, cfg) = tsrcConfigId

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
    name = propNameKS(qkKeyBase, run, tsrcConfigId)

    # Store propagators in subdirectories labeled by the configuration ID
    configID = codeCfg(suffix, cfg)
    remotePath = prop['subdirs'] + [configID]
    propFiles[qkKeyBase] = StageFile(localRoot, None, root[prop['root']],
                                     remotePath, name, 'r', None, False)
    if propFiles[qkKeyBase].exist():
        load = (fileCmd['propKS']['load'],propFiles[qkKeyBase].path())
        save = ('forget_ksprop',)
#        save = (fileCmd['propKS']['save'], propFiles[qkKeyBase].path())
    else:
        load = ('fresh_ksprop',)
        save = (fileCmd['propKS']['save'], propFiles[qkKeyBase].path())
    deflate = None
    if param['eigen']['Nvecs'] > 0:
        deflate = quark['deflate']
    if param['residQuality'] == 'fine':
        residual = quark['residual_fine']
    else:
        residual = quark['residual_loose']
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
def applySinkOp(param, work, quarks, quark, qkKeyMod, snkKeyMod, thisQ, wf1S, tsrc):
    """Apply sink operator"""

    ensemble = param['ensemble']
    fileCmd = param['fileCmd']

    # snkKeyMod typically has a structure like:
    # 2pt functions: 'd'
    # 3pt functions via extended propagator: 'ext,25,G5T-G5T,qheavy,0.257,-0.0433,1,1,0'
    tokens = splitSnkKey(snkKeyMod)
    if len(tokens) == 1:
        # 2pt function
        (smSnk, extT, stP, qkP, mQkP, epsP) = (snkKeyMod, None, None, None, None, None)
    elif len(tokens) == 6:
        # extended propagator, no additional momentum for "mother" quark
        (smSnk, extT, stP, qkP, mQkP, epsP) = tokens
        Bmomentum = [0, 0, 0]
    elif len(tokens) == 9:
        # extended propagator, with additional momentum for "mother" quark
        (smSnk, extT, stP, qkP, mQkP, epsP) = tokens[:6]
        Bmomentum = [int(val) for val in tokens[6:]]
    else:
        raise ValueError("Unexpected snkKeyMod", snkKeyMod)
    # try:
    #     (smSnk, extT, stP, qkP, mQkP, epsP) = splitSnkKey(snkKeyMod)
    # except ValueError:
    #     (smSnk, extT, stP, qkP, mQkP, epsP) = (snkKeyMod, None, None, None, None, None)

    save = ('forget_ksprop',)
    if smSnk == '1S':
        label = smSnk
        afm = ensemble['atrue']
        stride = param['KSaction']['stride']
        load = (fileCmd['wf']['load'], wf1S.path())
        thisQ = RadialWavefunctionSink(thisQ, label, afm, stride, load, save)
    elif smSnk == 'ext':
        # Bmomentum = [0, 0, 0]
        label = 'x'
        save = ['forget_ksprop', ]
        T = int(extT)
        t = ( tsrc + T ) % ensemble['dim'][3]

        # Make key for extended source
        snkKeyExt = makeSnkKey((smSnk, extT, stP, qkP))
        tokens = splitQuarkKey(qkKeyMod)
        if len(tokens) == 7:
            (residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, _) = tokens
        elif len(tokens) == 8:
            (residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, _, _) = tokens
        else:
            raise ValueError("Unrecognized quark key")
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
        if param['residQuality'] == 'fine':
            residual = quarkP['residual_fine']
        else:
            residual = quarkP['residual_loose']
        thisQ = KSInverseSink(q, mQkP, epsP, u0, quarkP['maxCG'], deflate, residual,
                              quarkP['precision'], twist, label, save)
    else:
        print("Unrecognized sink smearing", smSnk, "in", qkKeyMod)

    quarks[qkKeyMod] = work.addQuark(thisQ)

######################################################################
def createKSQuarks(param, work, sources, quarkKeys, rwParams, rndSq, wf1S, tsrcConfigId):
    """For ks_spectrum code: Create staggered quark propagators for tying together to make hadrons"""
    def assemble_tokens(residQuality, qk, m, eps, rnd, srcKey, smSnk, twist):
        """
        Line up the 'tokens' necessary to build a quark key
        """
        if twist:
            tokens = (residQuality, qk, m, eps, rnd, srcKey, smSnk, twist)
        else:
            tokens = (residQuality, qk, m, eps, rnd, srcKey, smSnk)
        return tokens

    def unpack(qkKey):
        tokens = splitQuarkKey(qkKeyMod)
        if len(tokens) == 7:
            (residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, snkKeyMod) = tokens
            twist = None
        elif len(tokens) == 8:
            (residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, snkKeyMod, twist) = tokens
        else:
            raise ValueError("Unrecognized quark key")
        return (residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, snkKeyMod, twist)


    (tsrc, suffix, cfg) = tsrcConfigId

    # Table of propagator files
    propFiles = dict()

    # Table of quark objects for each quark key
    quarks = dict()

    srcKeyModLast = ''
    twistLast = ''
    # Run through the quark keys, sorted so multiple masses with the
    # same source appear together.  Grouping them in this way allows
    # the MILC ks_spectrum code to use the multimass inverter.
    for qkKeyMod in sorted(quarkKeys, key=cmp_to_key(cmpQuarkKeys2)):
        (_, qk, mass, naik_epsilon, rndId, srcKeyMod, snkKeyMod, twist) = unpack(qkKeyMod)
        (_, momKey) = splitSrcKey(srcKeyMod)  # e.g., 'd.1.2.3' --> 'd', '1.2.3.'

        # Call for the point source first if it is unknown
        srcKeyBase = makeSrcKey(('d', momKey ))
        ptSrc = makeBaseSource(work, sources, srcKeyBase, rwParams, param['fileCmd'], rndSq, tsrc)

        # Modified source, if needed
        thisSrc = makeModifiedSource(param, work, sources, ptSrc, srcKeyMod, param['fileCmd'], wf1S)

        # Compute propagator from this source if we don't already have the file
        # Start with the basic propagator without any sink treatment
        residQuality = param['residQuality']
        tokens = assemble_tokens(residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, 'd', twist)
        qkKeyBase = makeQuarkKey(tokens)

        if 1:
            # Build the solve set (multimass version)

            if (srcKeyMod != srcKeyModLast) or (twist != twistLast):
                # When the source changes, add the previous solve set

                if len(srcKeyModLast) > 0:
                    work.addPropSet(thisSet)
                thisSet = startKSSolveSet(param, qk, thisSrc, twist)
                srcKeyModLast = srcKeyMod
                twistLast = twist
        else:
            raise ValueError("How did I get here? Single-mass version is never intended to be used.")
            # # Build the solve set (single-mass version)

            # if len(srcKeyModLast) > 0:
            #     work.addPropSet(thisSet)
            # thisSet = startKSSolveSet(param, qk, thisSrc, twist)
            # srcKeyModLast = srcKeyMod

        thisQ = solveKSProp(param, work, thisSet, propFiles, quarks, quarkKeys,
                            qk, mass, naik_epsilon, qkKeyBase, thisSrc, tsrcConfigId)

        # Do sink treatment on propagator if we don't have the result already
        if qkKeyMod not in quarks.keys():
            applySinkOp(param, work, quarks, param['quarks'][qk], qkKeyMod, snkKeyMod, thisQ, wf1S, tsrc)

    # Add the last propagator set
    if len(srcKeyModLast) > 0:
        work.addPropSet(thisSet)

    return ( quarks, propFiles )

######################################################################
def createCorrelators(param, work, quarks, correlators, rwParams, fileCmd, tsrc):
    """Tie quark propagators together to create npts"""

    (rwNcolor, rwNorm, rwSubset, scaleFactor, rwLabel) = rwParams
    for corr in correlators:
        # will need both momenta here --> parent and daughter
        (corrFile, QKey, aQKey, Qmom, aQmom, corrAttrs) = corr
        momentum_transfer = np.array(Qmom) + np.array(aQmom)  # TODO: Or is this be a minus sign?
        # To conserve momentum, the total momentum transfer injected at the current must balance
        # the momentum of the parent quark and the momentum of the daughter quark.
        om = -momentum_transfer
        # om = oppMom(mom)
        # pmom = "p{0:d}{1:d}{2:d}".format(*tuple(mom))
        # postfix = "-".join([pmom,param['residQuality']])
        # e.g., "p000-fine" or "p000-k123-fine"
        if np.all(np.array(aQmom) == np.array([0, 0, 0])):
            # "p123-fine"
            postfix = "-".join([
                "p{0:d}{1:d}{2:d}".format(*Qmom).replace("-", "m"),
                param['residQuality']])
        else:
            # "p123-k456-fine"
            postfix = "-".join([
                "p{0:d}{1:d}{2:d}".format(*Qmom).replace("-", "m"),
                "k{0:d}{1:d}{2:d}".format(*aQmom).replace("-", "m"),
                param['residQuality']])

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
        tokens = splitQuarkKey(qkKeyMod)
        if len(tokens) == 7:
            (_, qk, mass, naik_epsilon, rndId, srcKeyMod, _) = tokens
            twist = None
        elif len(tokens) == 8:
            (_, qk, mass, naik_epsilon, rndId, srcKeyMod, _, twist) = tokens
        else:
            raise ValueError("Unrecognized quark key")
        if param['quarks'][qk]['type'] == 'KS':
            (smSrc, momKey) = splitSrcKey(srcKeyMod)
            hisqProps = param['hisqProps']
            if twist is None:
                appendUnique(hisqProps, [smSrc, rndId, momKey, mass, naik_epsilon, qk] )
            else:
                appendUnique(hisqProps, [smSrc, rndId, momKey, mass, naik_epsilon, qk, twist] )

######################################################################
def rebuildKSQuarkKeys(param, quarkKeys):
    """Reconstruct list of KS quark keys from light propagator list"""

    residQuality = param['residQuality']
    hisqProps = param['hisqProps']
    for hisqProp in hisqProps:
        if hisqProp == 6:
            (smSrc, rndId, momKey, mass, naik_epsilon, qk) = hisqProp
            twist = None
        elif hisqProp == 7:
            (smSrc, rndId, momKey, mass, naik_epsilon, qk, twist) = hisqProp
        srcKeyMod = makeSrcKey([smSrc, momKey])
        # For generating KS propagators, we choose only a point sink 'd'
        if twist is None:
            qkKeyMod = makeQuarkKey([residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, 'd'])
        else:
            qkKeyMod = makeQuarkKey([residQuality, qk, mass, naik_epsilon, rndId, srcKeyMod, 'd', twist])
        appendUnique(quarkKeys, qkKeyMod)

######################################################################
def createMILCprompts(param, nstep, tsrc, tsrc0, kjob, seriesCfg, njobs):
    """Create MILC prompts based on YAML file.  Do this for this cfg, tsrc, and nstep"""

    suffix, cfg = decodeSeriesCfg(seriesCfg)
    tsrcConfigId = (tsrc, suffix, int(cfg))
    # In case of multijob,we create symlinks with a base name followed by .jnn
    # We use tsrc0 in the base name
    tsrcConfigIdSym = (tsrc0, suffix, int(cfg))

    # Construct job stdio, stdout, stderr, log file
    (stdin, stdout, stderr, stdlog) = setUpJobIOFiles(param, nstep, tsrcConfigId,
                                                      tsrcConfigIdSym, kjob, njobs )

    # Stage lattice file
    (latCoul, loadLat, saveLat, gFix) = stageLattice(param, suffix, cfg)

    # Stage eigenpair file
    (eigenPair, loadEigen, saveEigen) = stageEigen(param, suffix, cfg)

    # Fetch 1S wavefunction file
    wf1S = fetchWF(param)

    # Random source
    (rndSq, rndDq, rndQ, rndAq) = prepareRandomSource(param, tsrcConfigId)

    # Start input parameter set.  Prompt information is accumulated in "work".
    work = initializePrompts(param, tsrcConfigId)

    # Construct tables of propagators to be generated and correlators
    # to be computed
    quarkKeys = list()   # List of propagaator attributes including extended props
#    if param['scriptMode'] == 'KSproduction':
#        rebuildKSQuarkKeys(param, quarkKeys)

    correlators = list() # List of hadron npt correlators
    compile2ptCorrelators( param, correlators, quarkKeys, rndQ, rndAq, nstep, tsrcConfigId)
    compile3ptCorrelators( param, correlators, quarkKeys, rndQ, rndAq, nstep, tsrcConfigId)

    # Each entry in correlators is a list with contents
    # [
    # <allHISQFilesNoHiddenSSD.StageFile object at 0x10f1fe650>,
    # 'loose+qlight+0.0008+0.+q+d.1,0,0+d',
    # 'loose+qlight+0.0008+0.+q+d.0,0,0+ext,
    # 25,
    # G5T-G5T,
    # qheavy,
    # 0.257,
    # -0.0433',
    # [1, 0, 0],
    # [['A4-A4_V4-V4_T25_m0.257', -1, 'GT-GT'], ['A4-A4_T14-V4_T25_m0.257', 1, 'GXT-GT']]
    # ]
    # Each entry in quarkKeys is a single long string
    # The string is delimited by plus signs ("+") and typically looks somehting like:
    # 'loose+qheavy+0.257+-0.0433+q+d.0,0,0+d'
    # or
    # 'loose+qlight+0.0008+0.+q+d.0,0,0+ext,25,G5-G5,qheavy,0.257,-0.0433'

    for key in quarkKeys:
        print(key)
    print()
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
                                             tsrcConfigId)

    # Construct quark propagators (including extended ones) from the quark key list
    (quarks, propFiles) = createKSQuarks(param, work, sources, quarkKeys,
                                         rwParams, rndSq, wf1S, tsrcConfigId)

    # Create correlators
    createCorrelators(param, work, quarks, correlators, rwParams, param['fileCmd'], tsrc)

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
                         name, 'r', None, False)
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
        print(cmd,file=open(stdlog.path(),'a'))
        return
    else:
        try:
            reply = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print("ERROR: ", mpirun, "exited with code", e.returncode, ".")
            print( "output was" )
            print( e.output.decode() )
            print( "stdout was" )
            print( e.stdout.decode() )
            if e.stderr != None:
                print( "stderr was" )
                print( e.stderr.decode() )
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
def doJobSteps(param, tsrcs, njobs, seriesCfgsrep, asciiIOFileSets,
               binIOFileSets):
    """Do the job steps for the given base source time"""

    # FOR TSM TUNING ONLY!!
    # tsrcs = [ 0 ] * njobs

    # Job steps for all cfgs in this group
    steprange = param['job']['steprange']
    for nstep in range(steprange['low'], steprange['high']):

        print(datetime.now(),"Processing", param['scriptMode'], seriesCfgsrep, "for step", nstep, "tsrc", tsrcs)

        # Create MILC prompts and filenames for all cfgs in
        # this group for these tsrcs and all steps
        for kjob in range(njobs):
            print(datetime.now(),"Creating MILCprompts for job",kjob)
            seriesCfg = seriesCfgsrep[kjob]
            # For multijob compatiblity, the base name is based on the first tsrc
            a, b = createMILCprompts(param, nstep, tsrcs[kjob], tsrcs[0], kjob, seriesCfg, njobs)
            seriesCfgSrc = encodeSeriesCfgSrc(seriesCfg,str(tsrcs[kjob]))
            asciiIOFileSets[seriesCfgSrc] = a
            binIOFileSets[seriesCfgSrc] = b

        # Launch the job for this group (unless we are just scanning)
        # For multijob compatibility, use the first entry in the list for stdin, stdout, stderr
        if param['scriptMode'] != 'KSscan':
            print(datetime.now(),"Launching set", seriesCfgsrep, "for step", nstep, "tsrcs", tsrcs)
            status = launchJob(param,
                               asciiIOFileSets[encodeSeriesCfgSrc(seriesCfgsrep[0],str(tsrcs[0]))], njobs)

            # List files created
            if param['files']['root']['local'] != None:
                cmd = ' '.join(['ls', '-l',  param['files']['root']['local']+'/*'])
                try:
                    subprocess.check_output(cmd, shell=True)
                except subprocess.CalledProcessError as e:
                    print("Error listing files.  Return code", e.returncode)

            # Resolve symlinks and store all result files, propagators, sources, etc.
            for seriesCfgSrc in sorted(asciiIOFileSets.keys()):
                series, cfg, tsrca = decodeSeriesCfgSrc(seriesCfgSrc)
#                print(datetime.now(),"Storing files for", series, cfg)
                storeFiles(param, asciiIOFileSets[seriesCfgSrc], binIOFileSets[seriesCfgSrc])
                purgeProps(binIOFileSets[seriesCfgSrc])  # TEMPORARY

            if status == 1:
                print("Quitting due to errors")
                sys.exit(1)

############################################################
def runParam(seriesCfgs, ncases, njobs, param):
    """Run with the given parameter set"""

    # Configurations are processed in groups of njob independent parallel computations (multijob)
    # There are nreps such groups
    nreps = ncases // njobs

    # For each configuration we run several source times and do the work in nstep steps

    # Run through groups of configurations
    for irep in range(nreps):

        asciiIOFileSets = dict()
        binIOFileSets = dict()
        tarFileSets = dict()

        # List of cfgs to process in parallel (multijob) in this group
        seriesCfgsrep = seriesCfgs[irep*njobs:(irep+1)*njobs]

        # Create the tarfiles for all cfgs in this group
        for seriesCfg in seriesCfgsrep:
            tarFileSets[seriesCfg] = defineTarFile(param, seriesCfg)

        tsrcRange = param['tsrcRange']['loose']
        trange = range(tsrcRange['start'], tsrcRange['stop'], tsrcRange['step'])
        precessLoose = tsrcRange['precess']
        stepLoose = tsrcRange['step']

        # Construct a list of loose and fine precession shifts for each configuration
        tShiftLoose = [ 0 ] * njobs
        for kjob in range(njobs):
            suffix, cfg = decodeSeriesCfg(seriesCfgsrep[kjob])
            if len(suffix) == 0:
                suffix = 'a'
            cfgSep = param['cfgsep'][suffix]
            tShiftLoose[kjob] = int(cfg)//cfgSep * precessLoose

        # Loose calculation -- Iterate over all source times
        param['residQuality'] = 'loose'
        for tsrcBase in trange:
            tsrcs = [ tsrcBase ] * njobs
            nt = param['ensemble']['dim'][3]
            for kjob in range(njobs):
                tsrcs[kjob] = (tsrcBase + tShiftLoose[kjob]) % nt

            print(datetime.now(),"Loose calculation with tsrcs", tsrcs)
            sys.stdout.flush()
            doJobSteps(param, tsrcs, njobs, seriesCfgsrep, asciiIOFileSets, binIOFileSets)

        # Fine calculation -- only one source time per lattice
        # If we are running partial t ranges with multijob,
        # one job per lattice, we want all job components to do
        # their fine solves together or not at all.
        tsrcRange = param['tsrcRange']['fine']
        trange = range(tsrcRange['start'], tsrcRange['stop'], tsrcRange['step'])
        precessFine = tsrcRange['precess']

        # Construct a list of loose and fine precession shifts for each configuration
        tShiftFine = [ 0 ] * njobs
        for kjob in range(njobs):
            suffix, cfg = decodeSeriesCfg(seriesCfgsrep[kjob])
            if len(suffix) == 0:
                suffix = 'a'
            cfgSep = param['cfgsep'][suffix]
            tShiftFine[kjob] = int(cfg)//cfgSep * precessFine * stepLoose

        param['residQuality'] = 'fine'
        for tsrcBase in trange:
            tsrcs = [ tsrcBase ] * njobs
            nt = param['ensemble']['dim'][3]
            for kjob in range(njobs):
                tsrcs[kjob] = ( tsrcBase + tShiftLoose[kjob] + tShiftFine[kjob] ) % nt

            print(datetime.now(), "Fine calculation with tsrcBase", tsrcs)
            sys.stdout.flush()
            doJobSteps(param, tsrcs, njobs, seriesCfgsrep, asciiIOFileSets, binIOFileSets)

        if param['scriptMode'] != 'KSscan':
            # Create and store tar files, one for each cfg
            for seriesCfg in seriesCfgsrep:
                print("Storing tar files for", seriesCfg)
                storeTarFile(param, seriesCfg, tarFileSets[seriesCfg])

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
def initParam(param):
    """Set some initial values of params"""

    # Add the remote and archive roots to the yaml-generated dictionary:
    addRootPaths(param)

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
        job['id'] = 'debug'
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
def loadParams(YAMLAll, YAMLLaunch, YAMLEns, YAMLMachine):
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
    initParam(param)

    return param

############################################################
def main():

    # Set permissions
    os.system("umask 022")

    # Command-line args:
    if len(sys.argv) < 7:
        print(sys.argv)
        print("Usage", sys.argv[0], "<cfgs> <ncases> <njobs> <yaml> <yaml-launch> <yaml-ens> <yaml-machine>")
        sys.exit(1)

    # Decode arguments
    # cfgList     List of configuration numbers to run
    # ncases      Number of cases to process
    # njobs       Number of simultaneous cases in this partition
    # YAML        Basic parameter file in yaml format
    # YAMLEns     Ensemble parameter file in yaml format
    # YAMLMachine Machine/installation parameter file in yaml format

    (cfgList, ncases, njobs, YAML, YAMLLaunch, YAMLEns, YAMLMachine) = sys.argv[1:8]

    seriesCfgs = cfgList.split("/")
    ncases = int(ncases)
    njobs = int(njobs)

    print("Have args", cfgList, ncases, njobs, YAML, YAMLLaunch, YAMLEns, YAMLMachine)

    if ncases % njobs != 0:
        print("ERROR: Number of cases", ncases, "must be divisible by the number of jobs", njobs)
        sys.exit(1)

    # Load the basic parameter set
    param = loadParams(YAML, YAMLLaunch, YAMLEns, YAMLMachine)

    # We generate the non-extended staggered propagators first.  So we
    # need to collect a shopping list of propagators.  The list is
    # created by scanning the heavylight 2pt and 3pt correlators and
    # listing what is needed.  The shopping list is put in hisqProps.
    param['scriptMode'] = 'KSscan'
    param['hisqProps'] = list()

    print("Scanning with the parameter set", YAML)
    sys.stdout.flush()
    runParam(seriesCfgs, ncases, njobs, param)

    # Dump the collected propagator list
    hisqProps = param['hisqProps']
    for hisqProp in sorted(hisqProps):
        print(hisqProp)

    print("#############################################")

    # Now generate the hisq staggered propagators, two-points,
    # and three-points based on the shopping list "hisqProps"

    # Restore the initial parameter set
    param = loadParams(YAML, YAMLLaunch, YAMLEns, YAMLMachine)

    # Switch from KSscan to KSproduction mode
    param['scriptMode'] = 'KSproduction'

    # Add the shopping list
    param['hisqProps'] = hisqProps

    print("Running with the parameter set", YAML)
    sys.stdout.flush()
    runParam(seriesCfgs, ncases, njobs, param)

    sys.exit(0)

############################################################
main()
