#!/bin/bash
cd /home/avaiman/workspace/test/backend
export PYTHONPATH=$PYTHONPATH:.
source venv/bin/activate
python3 app/db/seed.py
