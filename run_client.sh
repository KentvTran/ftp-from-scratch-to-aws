#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=.
python3 -m client.ftp_client "$@"

