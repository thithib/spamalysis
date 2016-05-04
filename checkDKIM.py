#!/usr/bin/python3.4                                                                   
# -*-coding:Utf-8 -*    

import subprocess as sp
import re
import ipaddress



def checkDkim(mailHeaders):
    """Check if Dkim received allows a dns querry for public key, check as well the size of rsa encryption"""
    receivedDkim = mailHeaders['DKIM-Signature']
    if not receivedDkim:
        return 'EMPTY'
    try:
        dkimSelector = re.search('(s=[^\s]*)', receivedDkim).group(1)
    except AttributeError:
        dkimSelector=''
    if dkimSelector:   
        dkimSelector = dkimSelector.split(';')	
        dkimSelector = dkimSelector[0].split('s=')
        dkimSelector = dkimSelector[1]
    else:
        return 'Wrong Dkim format'
    try:
        domainName = re.search('(d=[^\s]*)', receivedDkim).group(1)
    except:
        print('Domain except')
        domainName=''
    if domainName:
        domainName = domainName.split(';')
        domainName = domainName[0].split('d=')
        domainName = domainName[1]
    digParam = dkimSelector + '._domainkey.' + domainName
    if  digParam:
        try:
            digResult = sp.check_output(["dig","+short","TXT",digParam]).decode("ascii")
        except sp.CalledProcessError:
            return 'EMPTY'
    try:
        dkimKey = re.search('(p=[^\s]*)', digResult).group(1)
    except:
        print('Regex Failed')
        dkimKey = ''
    if dkimKey:
        try:
            dkimKey = dkimKey.split('"')
        except:
            return 'EMPTY'
        try:
            dkimKey = dkimKey[0].split('p=')
        except:
            return 'EMPTY'
        dkimKey = dkimKey[1]
        dkimKey = re.sub("(.{78})", "\\1\n", dkimKey, 0, re.DOTALL)
        dkimKey = '-----BEGIN PUBLIC KEY-----\n' + dkimKey + '\n-----END PUBLIC KEY-----'
        try:
            f = open('/tmp/tempKey.pub','w')
        except:
            print('Could not open file')
            return 'EMPTY'
        try:
            f.write(dkimKey)
        except:
            print('Could not write in file')
            return 'EMPTY'
        try:
            f.close()
        except:
            print('Could not close file')
            return 'EMPTY'
        try:
            openSslResult = sp.check_output(["openssl","rsa","-noout","-text","-pubin","-in","/tmp/tempKey.pub"]).decode("ascii")
        except:
            print('Something went wrong with openssl')
            return 'EMPTY'
        try:
            openSslResult = openSslResult.split('(')
        except:
            return 'EMPTY'
        try:
            openSslResult = openSslResult[1].split(')')
        except:
            return 'EMPTY'
        return openSslResult[0]
