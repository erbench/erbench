#!/bin/bash

# exit on ctrl+c
trap "exit" INT


# run ditto on all datasets
for ds in "d1_fodors_zagats" ; do
    sbatch --job-name "deepmatcher-$ds" ./deepmatcher.sh "../../datasets/$ds/db_split/" "../../output/deepmatcher/$ds/" --embeddings "../../embeddings/" -e 40
done
