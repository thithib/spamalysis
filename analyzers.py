#!/usr/bin/python3.4
# _*_coding:Utf_8 _*
import re
import urllib3
import json

def emailAnalyzer(header):
    analyzed = re.search('([\w\.-]*)@([\w\.-]*)', header)
    email = analyzed.group()
    localpart = analyzed.group(1)
    domain = analyzed.group(2)
    location = locate(domain)
    return (email, localpart, domain, location)

def locate(domain):
    url = 'http://ip.pycox.com/json/' + domain
    headers = urllib3.make_headers()
    proxy = urllib3.ProxyManager('http://proxy.minet.net:82', proxy_headers=headers)
    r = proxy.request('GET', url)
    result = json.loads(str(r.data.decode('iso-8859-1')))
    location = ""
    if 'q' in result:
        longitude = result['longitude']
        latitude = result['latitude']
        location = str(latitude) + ',' + str(longitude)

    return location
