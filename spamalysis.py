#!/usr/bin/python3.4
# -*-coding:Utf-8 -*

import sys
import os

from parser import parseMail
from indexer import indexMail

def usage():
    print("usage " + sys.argv[0] + " <email directory> " + \
            "<ES node IP address> <ES node API listening port>\n" + \
            "Parses all mails in this directory (recursively) and indexes them in an elasticsearch cluster")
    exit(1)

def main():
    if len(sys.argv) < 3:
        usage()

    for root, dirs, files in os.walk(str(sys.argv[1])):
        for filename in files:
            if filename.endswith(".mail"):
                fullFilename = os.path.join(root, filename)
                indexName = fullFilename.split('/')[-2]
                with open(fullFilename, 'r', encoding = "ISO-8859-1") as f:
                    rawMail = f.read()
                jsonMail = parseMail(rawMail)
                if jsonMail:
                    if not indexMail(jsonMail, indexName, str(sys.argv[2]), str(sys.argv[3])):
                        sys.stderr.write("Error when indexing mail " + fullFilename + "\n")
                else:
                    sys.stderr.write("Error when parsing mail " + fullFilename + "\n")

if __name__ == "__main__":
    main()

