
source secrets.sh

curl  -F token=$SLACK_API_TOKEN -F file=@sample.mp4 -F filename=sample.mp4 -F channels='#bottest' "https://slack.com/api/files.upload"

