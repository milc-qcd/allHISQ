#! /bin/bash

# Clean up props and rands

# Usage ./purge_symlinks.sh <JobID>

JobID=$1

echo "Purging symlinks for JobID = $JobID"
find -P run?/logs -lname '?*Job'${JobID}'*' -exec /bin/rm '{}' \;


