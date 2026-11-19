#! /bin/bash

while read -r line
do
    set ${line}
    sc=$1
    ts=$2
    status=$3
    jid=$4
    jseq=$5
    if [ -z "${status}" ]
    then
	echo ${line}
	continue
    fi
    
    # Change seriescfg format
    seriescfg=`echo $sc | awk -F. '{printf("%s%06d",$1,$2)}'`
    tsrc=`echo $ts | awk -F. '{printf("%s%03d",$1,$2)}'`

    # If tarfile exists, then mark it X and go on
    list=`ls run3/${seriescfg}/tar/Job*_${tsrc}_${seriescfg}.tar.bz2`
    if [ $? -ne 0 ]
    then
	tarfile=""
    else
	tarfile=`echo "${list}" | tail -n 1`
    fi

    if [ -n "${tarfile}" ]
    then
	# Get jid from file name
	jidnew=`echo ${tarfile} | awk '{j=index($1,"Job")+3;s=substr($1,j,length($1)-j);k=index(s,"_")-1;print substr(s,1,k)}'`
	if [ "${jid}" != "${jidnew}" ]
	then
	    echo ${seriescfg} Changing ${jid} to ${jidnew}
	fi
	echo "${sc} ${ts} X ${jidnew} ${jseq}"
	continue
    fi

    # Look for run log directory
    runpath=run3/${seriescfg}/${tsrc}/logs
    if [ -d ${runpath} ]
    then
	# Found run log. Mark as queued
	echo Found ${runpath}
	if [ -n "${jid}" ]
	then
	    # If we already have a jid, write it
	    echo "${sc} ${ts} Q ${jid} ${jseq}"
	else
	    # Get the jid from the step0 input file
	    infile=`ls ${runpath}/inJob*_step0_* | tail -n 1`
	    if [ -n "${infile}" ]
	    then
		jid=`grep job_id ${infile} | awk -F. '{print $2}'`
		# Get the jseq from the step0 input file name
		jseq=`basename ${infile} | awk -F_ '{print substr($1,6,length($1)-6)}'`
		echo "${sc} ${ts} Q ${jid} ${jseq}"
	    else
		# Best to rerun the job if the infile is missing
		echo "${sc} ${ts} XXtar"
	    fi
	fi
	continue
    fi

    # Look for check file
    checkpath=check/check_${sc}_${ts}
    if [ -f ${checkpath} ]
    then
	echo Found ${checkpath}
	# If checked, look for fail directory for this run
	failpath=run3/${seriescfg}/fail/${jid}/${tsrc}
	# If fail path exists, then mark it XXfix
	if [ -d ${failpath} ]
	then
	    echo "${sc} ${ts} XXfix ${jid} ${jseq}"
	    continue
	fi
    fi

    # No trace of job, echo input
    echo "${sc} ${ts} ${status} ${jid} ${jseq}"

done
