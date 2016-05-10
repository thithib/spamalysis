#!/usr/bin/python3.4                                                                   
# -*-coding:Utf-8 -*    

import subprocess as sp
import re
import ipaddress



def checkSpf(mailHeaders):
    """Check if Ip from SPF received is in dig querry"""
    receivedSpf = mailHeaders['Received-SPF']
    if receivedSpf:
        if re.search('(fail)',receivedSpf).group(1):
            return 'Fail'
        elif re.search('(softfail)',receivedSpf).group(1):
            return 'Soft Fail'
        elif re.search('(neutral)',receivedSpf).group(1):
            return 'Neutral'
        elif re.search('(PermError)',receivedSpf).group(1):
            return 'PermError'
        elif re.search('(TempError)',receivedSpf).group(1):
            return 'TempError'
        elif re.search('(pass)',receivedSpf).group(1):
            try:
                senderDomain = re.search('(\@[^\s]*)', receivedSpf).group(1)
            except AttributeError:
                # Domain not found in the original string
                senderDomain = '' # apply your error handling
            try:
                senderDomain = senderDomain.split('@')
            except AttributeError:
                senderDomain = '' #apply your error handling
                senderDomain = senderDomain[1].split(';')
            try:
                senderIp = re.search('(\client-ip=[^\s]*)',receivedSpf).group(1)
            except AttributeError:
                senderIp = '' # apply your error handling
                senderIp = senderIp.split('client-ip=')
                senderIp = senderIp[1].split(';')
            try:
                senderIp = ipaddress.ip_address(senderIp[0])
            except:
                senderIp = ''
            #print(senderIp[0])
            try:
                digResult = sp.check_output(["dig", "+short","TXT",senderDomain[0]]).decode("ascii")
            except sp.CalledProcessError:
                return 'PassNoDig'
            ipNetworks = re.findall( r'(([0-9]+(?:\.[0-9]+){3})+/+[0-9]{2})|([0-9]+(?:\.[0-9]+){3})', digResult )
            results = [t[0] for t in ipNetworks]
            #print(len(results))
            for i, val in enumerate(results):
                try:
                    network = val
                except:
                    network = ''
                    #print(network)
                if not network:
                    return 'PassUnchecked'
                else:	
                    try:
                        network = ipaddress.ip_network(network)
                        if senderIp in ipaddress.ip_network(network):
                            return 'PassUnchecked'
                        else:
                            if i == len(results):
                                return 'PassUnchecked'
                    except ValueError:
                        network = ipaddress.IPv6Interface(network)
                        if senderIp in network.network:
                            return 'PassTrue'
                        else:
                            if i== len(results):
                                return 'PassUnchecked'
