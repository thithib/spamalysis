#!/usr/bin/python3.4
# _*_coding:Utf_8 _*
import re
import maxminddb
import socket

def emailAnalyzer(header):
    analyzed = re.search('([\w\.-]*)@([\w\.-]*)', header)
    email = analyzed.group()
    localpart = analyzed.group(1)
    domain = analyzed.group(2)
    location = locate(domain)
    return (email, localpart, domain, location)

def locate(domain):
    try:
        ip = socket.gethostbyname(domain)
        database = maxminddb.open_database('/home/spamalysis/GeoLite2-City.mmdb')
        result = database.get(ip)
        if result == None:
            return str()
        database.close()
        longitude = result['location']['longitude']
        latitude = result['location']['latitude']
        location = str(latitude) + ',' + str(longitude)
        return location
    except socket.gaierror:
        return str()
