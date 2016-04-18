#!/usr/bin/python3.4
# -*-coding:Utf-8 -*

def processBody(mailBody, mailHeaders, html=True):
    """Search for some interesting content"""
    resultBody = dict()
    resultBody['body'] = mailBody
    return resultBody

