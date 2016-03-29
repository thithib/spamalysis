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
    """Parse the mail"""
    msg = email.message_from_string(rawMail)
    obj = dict()

    obj['X-Envelope-From'] = purgeBrackets(getMailHeader(msg.get('X-Envelope-From', ''))) or 'EMPTY'
    obj['X-Envelope-To'] = purgeBrackets(getMailHeader(msg.get('X-Envelope-TO', ''))) or 'EMPTY'
    obj['X-Spam-Flag'] = getMailHeader(msg.get('X-Spam-Flag', '')) or 'EMPTY'
    obj['X-Spam-Score'] = float(getMailHeader(msg.get('X-Spam-Score', '')))
    obj['To'] = purgeBrackets(getMailHeader(msg.get('To', ''))) or 'EMPTY'
    obj['Date'] = parseDate(getMailHeader(msg.get('Date', '')))
    obj['From'] = str(getMailHeader(msg.get('From', '')) or 'EMPTY')
    obj['Reply-To'] = str(getMailHeader(msg.get('Reply-To', '')) or 'EMPTY')
    obj['X-Priority'] = int((getMailHeader(msg.get('X-Priority', '')) or '0')[0])
    obj['MIME-Version'] = float(getMailHeader(msg.get('MIME-Version', '')))
    obj['Subject'] = getMailHeader(msg.get('Subject', '')) or 'EMPTY'
    obj['Content-Transfer-Encoding'] = getMailHeader(msg.get('Content-Transfer-Encoding', '')) or 'EMPTY'
    obj['Content-Type'] = getMailHeader(msg.get('Content-Type', '')) or 'EMPTY'

    return obj

