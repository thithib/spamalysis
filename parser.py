#!/usr/bin/python3.4
# -*-coding:Utf-8 -*

import re
import email
from email.utils import parseaddr
from email.header import decode_header


def getMailHeader(header_text, default="ascii"):
    """Decode header_text if needed"""
    try:
        if not header_text:
            return 'EMPTY'
        else:
            headers=decode_header(header_text)
    except email.Errors.Header.ParseError:
        #This already apend in email.base64mime.decode()
         #instead return sanitized ascii string
       return header_text.encode('ascii',errors='replace').decode('ascii')
    else:
        for i,(text,charset) in enumerate(headers):
            try:
                if(charset!=None):
                    headers[i]=str(text,charset)
                else:
                    headers[i]=text
            except LookupError:
                #if the charset is unknown, force default
                headers[i]=str(text,default,errors='replace')
        return headers[i]

def purgeBrackets(string):
    """Get rid of <> around a string"""
    if not string:
        return 'ERROR_EMPTY_STRING'
    else:
        string = string.replace("<","").replace(">","")
        return string

def parseMail(rawMail):
    """Parse the mail"""
    msg=email.message_from_string(rawMail)
    obj={'X-Envelope-From': purgeBrackets(getMailHeader(msg.get('X-Envelope-From',''))),
        'X-Envelope-To': purgeBrackets(getMailHeader(msg.get('X-Envelope-TO',''))),
        'X-Spam-Flag': getMailHeader(msg.get('X-Spam-Flag','')),
        'X-Spam-Score': float(getMailHeader(msg.get('X-Spam-Score',''))),
        'To': getMailHeader(msg.get('To','')),
        'Date': getMailHeader(msg.get('Date','')),
        'From': getMailHeader(msg.get('From','')),
        'Reply-To': getMailHeader(msg.get('Reply-To','')),
        'X-Priority': int(getMailHeader(msg.get('X-Priority',''))),
        'MIME-Version': float(getMailHeader(msg.get('MIME-Version',''))),
        'Subject': getMailHeader(msg.get('Subject','')),
        'Content-Transfer-Encoding': int(getMailHeader(msg.get('Content-Transfer-Encoding','')).replace("bit", "")),
        'Content-Type': getMailHeader(msg.get('Content-Type',''))
        }
    return obj

