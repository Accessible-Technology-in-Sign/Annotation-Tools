#!/bin/bash

# (Bill): I realize how awfully ugly the previous decode scripts are
# so I tried to make this one less hideous

thread_count=32
#Directory where 
source_dir=/data/sign_language_videos/review_313/fourth_wave
dest_dir=/data/sign_language_videos/review_sets/review_313/review_7

#List of users whose stuff we are going to decore
declare -a users=("4a.2.1032" "4a.2.1042" "4a.2.1043" "4a.2.1047" "4a.2.1048" "4a.2.1049" "4a.2.1050" "4a.2.1051" "4a.2.1052" "4a.2.1054" "4a.2.1055" "4a.2.1057")

# get length of an array
numusers=${#users[@]}

# use for loop to read all values and indexes
for (( i=0; i<${numusers}; i++ ));
do
  #echo "${users[$i]}"
  python3 decode_split_by_length.py \
    --backup_dir $source_dir/"${users[$i]}" \
    --dest_dir $dest_dir \
    --make_sign_dirs \
    --num_threads $thread_count \
    --ffmpeg_loglevel quiet 1> $dest_dir/logs/"${users[$i]}".log 2> /tmp/garbage.txt
done


