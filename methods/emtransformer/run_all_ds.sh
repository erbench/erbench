#!/bin/bash

# exit on ctrl+c
trap "exit" INT

# "d1_fodors_zagats" "d2_abt_buy" "d3_amazon_google" "d4_dblp_acm" "d5_imdb_tmdb" "d6_imdb_tvdb" "d7_tmdb_tvdb" "d8_amazon_walmart" "d9_dblp_scholar"
# run ditto on all datasets
for ds in "d1_fodors_zagats" "d2_abt_buy" "d3_amazon_google" "d4_dblp_acm" "d5_imdb_tmdb" "d6_imdb_tvdb" "d7_tmdb_tvdb" "d8_amazon_walmart" "d9_dblp_scholar"; do
    sbatch --job-name "emtransformer-$ds" ./emtransformer.sh "../../datasets/$ds/db_split/" "../../output/emtransformer/$ds/" -e 40
done
