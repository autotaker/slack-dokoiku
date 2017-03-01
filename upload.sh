#!/bin/bash
source secrets.sh

curl  -F token=$SLACK_API_TOKEN -F file=@$1 \
      -F filename=sample.mp4  \
      -F channels="$2" "https://slack.com/api/files.upload"

