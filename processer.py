#!/usr/bin/python3.4
# -*-coding:Utf-8 -*

import re

def processBody(mailBody, mailHeaders):
    """Search for some interesting content"""
    resultBody = dict()
    resultBody['phoneNumbers'] = processPhoneNumbers(mailBody)
    resultBody['URLs'] = processURLs(mailBody)
    return resultBody

def processPhoneNumbers(mailBody):
    """Get phone numbers from e-mail body"""
    phoneNumbers = list()
    r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    for part, html in mailBody:
        for x in r.findall(str(part)):
            phoneNumbers.append(x)
    return list(set(phoneNumbers))

def processURLs(mailBody):
    """Get URLs from e-mail body"""
    URLs = list()
    return URLs

