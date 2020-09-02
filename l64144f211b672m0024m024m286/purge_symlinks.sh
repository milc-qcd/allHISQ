#! /bin/bash

# Clean up props and rands

# Usage ./purge_symlinks.sh <JobID>

JobID=$1

echo "Purging symlinks for JobID = $JobID"
/bin/rm -f run3?/logs/loose/*Job${JobID}*.j??
/bin/rm -f run3?/logs/fine/*Job${JobID}*.j??
# find -P run3?/logs -lname '?*Job'${JobID}'*' -exec /bin/rm '{}' \;


