#! /bin/bash

ens=144288f211b700m000569m01555m1827
latpathin=lat/v5
proppath=prop
randpath=rand
latpathv5=../scratch/lat/v5
latpathape=../scratch/lat/ape
runjobpath=runJobScripts

count=1
oldseriescfg=""

# Run through todo file examining each finished job
grep -w X todo | while read -r line
do

    set $line
    sc=$1
    ts=$2
    jid=$4
    jseq=$5

    # Change seriescfg, tsrc format
    seriescfg=`echo $sc | awk -F. '{printf("%s%06d",$1,$2)}'`
    tsrc=`echo $ts | awk -F. '{printf("%s%03d",$1,$2)}'`

    # If lattice file is missing, assume already cleared
    latin=l${ens}${sc}
    path=${latpathin}/${latin}
    if [ ! -f ${path} ]
    then
	continue
    fi

#    # If seriecfg directory is missing, assume already processed
#    if [ ! -d ${proppath}/${seriescfg} ]
#    then
#	continue
#    fi

    # Count completed sources for this config
    if [ ${seriescfg} = "${oldseriescfg}" ]
    then
	count=$[${count}+1]
    else
	oldseriescfg=${seriescfg}
	count=1
    fi
	
    echo "Purging input files for ${sc} ${ts}" ${jid} ${jseq} count = ${count}

    # Remove props for this line
    path=${proppath}/${seriescfg}/${tsrc}
    if [ -d ${path} ]
    then
	./purge_all_props.sh ${sc} ${ts}
    fi

    # Remove rands for this line
    parh=${randpath}/${seriescfg}/${tsrc}
    if [ -d ${path} ]
    then
	echo Removing rand files
	/bin/rm -r ${path}
    fi

    # Remove run scripts for this line
    path=${runjobpath}/${jseq}
    if [ -n "${jseq}" ]
    then
	if [ -d ${path} ]
	then
	    echo Removing runJob files for ${jseq}
	    /bin/rm -r ${path}
	fi
    fi

    # If all sources are completed, delete the lattices
    # and prop and rand dirs
    if [ ${count} -eq 24 ]
    then
        path=${latpathin}/${latin}
	echo Removing ${path}
	/bin/rm ${path}

	path=${proppath}/${seriescfg}
	if [ -d ${path} ]
	then
	    echo Removing ${path}
	    rm -r ${path}
	fi
	
	path=${randpath}/${seriescfg}
	if [ -d ${path} ]
	then
	    echo Removing ${path}
	    rm -r ${path}
	fi
	
	path=${latpathv5}/${latin}
	if [ -f ${path}.vol0000 ]
	then
	    echo Removing ${path}.vol0000, etc.
	    /bin/rm ${path}*
	fi

	ape=ape${ens}${sc}
	path=${latpathape}/${ape}
	if [ -f ${path}.vol0000 ]
	then
	    echo Removing ${path}.vol0000, etc.
	    /bin/rm ${path}*
	fi
    fi
done


