#!/usr/bin/python3.4
# -*-coding:Utf-8 -*

import re
import email
from time import strptime, strftime
from email.utils import parseaddr
from email.header import decode_header


def getMailHeader(header_text, default="ascii"):
    """Decode header_text if needed"""
    try:
        if not header_text:
            return False
        else:
            headers = decode_header(header_text)
    except email.Errors.Header.ParseError:
        # This already apend in email.base64mime.decode()
         # instead return sanitized ascii string
       return header_text.encode('ascii', errors='replace').decode('ascii')
    else:
        for i, (text,charset) in enumerate(headers):
            try:
                if(charset != None):
                    headers[i] = str(text, charset)
                else:
                    headers[i] = text
            except LookupError:
                #if the charset is unknown, force default
                headers[i] = str(text, default, errors='replace')
        return headers[i]

def purgeBrackets(string):
    """Get rid of <> around a string"""
    if not string:
        return False
    else:
        string = string.replace("<", "").replace(">", "")
        return string

def parseDate(date):
    """Helper for date parsing"""
    parsedDate = str()
    try:
        parsedDate = strftime('%Y/%m/%d %H:%M:%S', strptime(date[0:-6], '%a, %d %b %Y %H:%M:%S'))
    except ValueError:
        pass
    finally:
        return parsedDate

def parseMail(rawMail):
    """Split headers and body and send them to the corresponding parser"""
    msg = email.message_from_string(rawMail)
    print(msg.keys())
    # Getting mail body requires a trick
    msgBody = str()
    if msg.is_multipart():
        for payload in msg.get_payload():
            msgBody += str(payload.get_payload())
    else:
        msgBody = msg.get_payload()

    # Headers are directly reachable
    jsonMail = parseHeaders(msg)
    jsonMail.update(parseBody(msgBody))

    return jsonMail

def parseHeaders(msg):
    """Parse mail headers into a dictionnary"""
    headers = dict()
    headers['X-Envelope-From'] = getMailHeader(msg.get('X-Envelope-From', '')) or 'EMPTY'
    headers['X-Envelope-To'] = getMailHeader(msg.get('X-Envelope-TO', '')) or 'EMPTY'
    headers['X-Spam-Flag'] = getMailHeader(msg.get('X-Spam-Flag', '')) or 'EMPTY'
    headers['X-Spam-Score'] = float(getMailHeader(msg.get('X-Spam-Score', '')))
    headers['To'] = getMailHeader(msg.get('To', '')) or 'EMPTY'
    headers['Date'] = parseDate(getMailHeader(msg.get('Date', '')))
    headers['From'] = str(getMailHeader(msg.get('From', '')) or 'EMPTY')
    headers['Reply-To'] = str(getMailHeader(msg.get('Reply-To', '')) or 'EMPTY')
    headers['X-Priority'] = int((getMailHeader(msg.get('X-Priority', '')) or '0')[0])
    headers['MIME-Version'] = str(getMailHeader(msg.get('MIME-Version', '')))
    headers['Subject'] = getMailHeader(msg.get('Subject', '')) or 'EMPTY'
    headers['Content-Transfer-Encoding'] = getMailHeader(msg.get('Content-Transfer-Encoding', '')) or 'EMPTY'
    headers['Content-Type'] = getMailHeader(msg.get_content_type()) or 'EMPTY'
    headers['Charset'] = getMailHeader(msg.get_content_charset('')) or 'EMPTY'
    headers['Received'] = str(msg.get_all('Received'))
    headers['Received-SPF'] = str(msg.get_all('Received-SPF','EMPTY')) #INTERESTING HEADER, Can be faked for badely configured gateway https://isc.sans.edu/diary/UPS+Malware+Spam+Using+Fake+SPF+Headers/17693
    headers['DKIM-Signature'] = str(msg.get('DKIM-Signature','EMPTY'))
    #print(headers['DKIM-Signature'])
    #print(headers['Received-SPF'])
    
    #TODO
    #headers['Content-Disposition'] = msg.get_content_disposition(msg) or 'EMPTY'
    #headers['Charsets'] = msg.get_charsets()
    #print(toto)
    #print(msg.get_all('Received'))
    boundary = msg.get_boundary('')
    return headers

def parseBody(mailBody):
    """Parse mail body"""
    body = dict()
    body['body'] = mailBody
    return body

