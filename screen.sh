#!/bin/sh
if[-z "$STY"];then exec screen -dm -S spamalysis /bin/bas "$0";fi
./spamalysis.py ../../spamalysis/spamarchive 192.168.103.98 9200
