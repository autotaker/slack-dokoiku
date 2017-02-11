#!/bin/bash
set -e
if [ ! -e env ]; then
    virtualenv env
fi
source env/bin/activate
pip install -r requirements.txt
sqlite3 db.sqlite < schema.sql
source secrets.sh
python dokoiku.py 
