#!/usr/bin/python3.4                                                                   
# -*-coding:Utf-8 -*    

import subprocess as sp
import re
import ipaddress



def checkDkim(mailHeaders):
    """Check if Dkim received allows a dns querry for public key, check as well the size of rsa encryption"""
    receivedDkim = mailHeaders['DKIM-Signature']
    dkimResult = dict()
    if not receivedDkim:
        dkimResult['dkimResult'] = 'Not DKIM signed'
        return dkimResult
    try:
        dkimSelector = re.search('(s=[^\s]*)', receivedDkim).group(1)
    except AttributeError:
        dkimResult['dkimResult'] = 'No DKIM selector'
        return dkimResult
    if dkimSelector:   
        dkimSelector = dkimSelector.split(';')	
        dkimSelector = dkimSelector[0].split('s=')
        dkimSelector = dkimSelector[1]
    else:
        dkimResult['dkimResult'] = 'Wrong DKIM format'
        return dkimResult
    try:
        domainName = re.search('(d=[^\s]*)', receivedDkim).group(1)
    except:
        dkimResult['dkimResult'] = 'DKIM selector but no domain'
        return dkimResult
    if domainName:
        domainName = domainName.split(';')
        domainName = domainName[0].split('d=')
        domainName = domainName[1]
    digParam = dkimSelector + '._domainkey.' + domainName
    if  digParam:
        try:
            digResult = sp.check_output(["dig","+short","TXT",digParam]).decode("ascii")
            dkimResult['dkimResult'] = 'DKIM OK'
        except sp.CalledProcessError:
            dkimResult['dkimResult'] = 'EMPTY'
            return dkimResult
    try:
        dkimKey = re.search('(p=[^\s]*)', digResult).group(1)
    except:
        dkimResult['dkimResult'] = 'DKIM OK'
        dkimResult['dkimKey'] = 'EMPTY'
        return dkimResult
    if dkimKey:
        try:
            dkimKey = dkimKey.split('"')
        except:
            dkimResult['dkimKey'] = 'EMPTY'
            return dkimResult
        try:
            dkimKey = dkimKey[0].split('p=')
        except:
            dkimResult['dkimKey'] = 'EMPTY'
            return dkimResult
        dkimKey = dkimKey[1]
        dkimKey = re.sub("(.{78})", "\\1\n", dkimKey, 0, re.DOTALL)
        dkimKey = '-----BEGIN PUBLIC KEY-----\n' + dkimKey + '\n-----END PUBLIC KEY-----'
        try:
            f = open('/tmp/tempKey.pub','w')
        except:
            #print('Could not open file')
            dkimResult['dkimKey'] = 'EMPTY'
            return dkimResult
        try:
            f.write(dkimKey)
        except:
            #print('Could not write in file')
            dkimResult['dkimKey'] = 'EMPTY'
            return dkimResult
        try:
            f.close()
        except:
            #print('Could not close file')
            dkimResult['dkimKey'] = 'EMPTY'
            return dkimResult
        try:
            openSslResult = sp.check_output(["openssl","rsa","-noout","-text","-pubin","-in","/tmp/tempKey.pub"]).decode("ascii")
        except:
            #print('Something went wrong with openssl')
            dkimResult['dkimKey'] = 'EMPTY'
            return dkimResult
        try:
            openSslResult = openSslResult.split('(')
        except:
            dkimResult['dkimKey'] = 'EMPTY'
            return dkimResult
        try:
            openSslResult = openSslResult[1].split(')')
        except:
            dkimResult['dkimKey'] = 'EMPTY'
            return dkimResult
        openSslResult = openSslResult[0].split('bit')
        openSslResult[0] = int(openSslResult[0])
        dkimResult['dkimKey'] = openSslResult[0]
        return dkimResult
