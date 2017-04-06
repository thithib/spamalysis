#!/usr/bin/python3.4
# _*_coding:Utf_8 _*
import re
import socket

def headerSanitizer(header):
    return re.findall('[\w\.-]*@[\w\.-]*', header)

def emailAnalyzer(header, database):
    analyzed = re.search('([\w\.-]*)@([\w\.-]*)', header)
    email = analyzed.group()
    localpart = analyzed.group(1)
    domain = analyzed.group(2)
    location = locate(domain, database)
    return (email, localpart, domain, location[0], location[1], location[2])

def emailAnalyzerReceived(header, database):
    res = header.rsplit('from', 2)[-1]
    analyzed = re.search('([^\s]+)', res)
    domain = analyzed.group()
    location = locate(domain, database)
    return (domain, location[0], location[1])

def getDate(header):
    if isinstance(header, str):
        res = header.rsplit('from', 2)[-1]
        analyzed = re.search('((?:Mon?|Tue?|Wed?|Thu?|Fri?|Sat?|Sun?),.*)', res)
        if analyzed:
            date = analyzed.group(0)
            date = date.split('\'')
            return date[0]
        else:
            return 'EMPTY'
    else:
        return 'EMPTY'

def locateIPv4(ip, database):
    return database.query(ip)

def locate(domain, database):
    domainType = detect(domain)

    if domainType == "IPv4":
        result = locateIPv4(domain, database)
    elif domainType == "valid_domain":
        try:
            ip = socket.getaddrinfo(domain,None,socket.AF_INET6)[0][4][0]
            return (str(), "IPv6", str())
        except socket.gaierror:
            ip = socket.gethostbyname(domain)
            result = locateIPv4(ip, database)
            domainType = "IPv4"
    else:
        return (str(), domainType, str())

    if result == None:
        return (str(), domainType, str())
    country_code = result['registered_country']['iso_code']
    longitude = result['location']['longitude']
    latitude = result['location']['latitude']
    location = str(latitude) + ',' + str(longitude)
    return (location, domainType, country_code)

def detect(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
        return "IPv6"
    except socket.error:
        try:
            socket.inet_aton(address)
            return "IPv4"
        except socket.error:
            try:
                socket.gethostbyname(address)
                return "valid_domain"
            except socket.gaierror:
                return "invalid_domain"

def fetchReceived(string):
    return re.findall('\[(([0-9]{1,3}.){3}.([0-9]{1,3}))\]', string)
