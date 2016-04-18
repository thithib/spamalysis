#!/usr/bin/python3.4
# _*_coding:Utf_8 _*
import re

def emailAnalyzer(email):
    analyzed = re.search('([\w\.-]*)@([\w\.-]*)', email)
    email = analyzed.group(0)
    localpart = analyzed.group(1)
    domain = analyzed.group(2)

    return (email,localpart, domain)
