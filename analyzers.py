#!/usr/bin/python3.4
# _*_coding:Utf_8 _*
import re
import socket

def emailAnalyzer(header, database):
    analyzed = re.search('([\w\.-]*)@([\w\.-]*)', header)
    email = analyzed.group()
    localpart = analyzed.group(1)
    domain = analyzed.group(2)
    location = locate(domain, database)
    return (email, localpart, domain, location[0], location[1])

def locateIPv4(ip, database):
    return database.query(ip)

def locate(domain, database):
    domainType = detect(domain)

    if domainType == "IPv4":
        result = locateIPv4(domain, database)
    elif domainType == "valid_domain":
        try:
            ip = socket.getaddrinfo(domain,None,socket.AF_INET6)[0][4][0]
            return (str(), "IPv6")
        except socket.gaierror:
            ip = socket.gethostbyname(domain)
            result = locateIPv4(ip, database)
            domainType = "IPv4"
    else:
        return (str(), domainType)

    if result == None:
        return (str(), domainType)

    longitude = result['location']['longitude']
    latitude = result['location']['latitude']
    location = str(latitude) + ',' + str(longitude)
    return (location, domainType)

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
    relays = []
    for match in re.finditer('\[(([0-9]{1,3}.){3}.([0-9]{1,3}))\]', string):
        relays.append(match)
    return relays
