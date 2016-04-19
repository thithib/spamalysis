#!/usr/bin/python3.4
# _*_coding:Utf_8 _*
import re

def emailAnalyzer(header):
    analyzed = re.search('([\w\.-]*)@([\w\.-]*)', header)
    return (analyzed.group(),analyzed.group(1),analyzed.group(2))
