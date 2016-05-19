#!/usr/bin/python3.4
# -*-coding:Utf-8 -*

import re
from time import strptime, strftime

import email
from email.utils import parseaddr
from email.header import decode_header

import decode
from processer import processBody, processAttachments

from checkSPF import checkSpf
from checkDKIM import checkDkim


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
    #Uncomment to show all header names
    #print(msg.keys())

    # Headers are directly reachable
    jsonMail = parseHeaders(msg)

    # Getting entire mail body is a bit harder
    msgBody = list()
    msgAttachments = list()
    for part in msg.walk():
        # multipart/* are just containers
        if part.is_multipart():
            continue
        contentDisposition = part.get('Content-Disposition')
        if contentDisposition == None or contentDisposition == 'inline':
            decodedPart = part.get_payload()
            if part.get("Content-Transfer-Encoding") == "quoted-printable":
                decodedPart = decode.decode_quote_printable_part(decodedPart)
            elif part.get("Content-Transfer-Encoding") == "base64":
                decodedPart = decode.decode_base64_part(decodedPart)
            if part.get_content_subtype() == "plain":
                msgBody.append((decodedPart, False))
            elif part.get_content_subtype() == "html":
                msgBody.append((decodedPart, True))
        else:
            # It is an attachment
            msgAttachments.append((part.get_filename(), part.get_payload(decode=True)))

    jsonMail.update(processBody(msgBody, jsonMail))
    jsonMail.update(processAttachments(msgAttachments))
    jsonMail.update(checkSpf(jsonMail))
    jsonMail.update(checkDkim(jsonMail))

    return jsonMail

def parseHeaders(msg):
    """Parse mail headers into a dictionnary"""
    headers = dict()
    headers['X-Envelope-From'] = str(getMailHeader(msg.get('X-Envelope-From', ''))) or 'EMPTY'
    headers['X-Envelope-To'] = str(getMailHeader(msg.get('X-Envelope-TO', ''))) or 'EMPTY'
    headers['X-Spam-Flag'] = str(getMailHeader(msg.get('X-Spam-Flag', ''))) or 'EMPTY'
    headers['X-Spam-Score'] = float(getMailHeader(msg.get('X-Spam-Score', '')))
    headers['To'] = str(getMailHeader(msg.get('To', ''))) or 'EMPTY'
    headers['Date'] = parseDate(str(getMailHeader(msg.get('Date', ''))))
    headers['From'] = str(getMailHeader(msg.get('From', '')) or 'EMPTY')
    headers['Reply-To'] = str(getMailHeader(msg.get('Reply-To', '')) or 'EMPTY')
    headers['X-Priority'] = int((getMailHeader(msg.get('X-Priority', '')) or '0')[0])
    headers['MIME-Version'] = str(getMailHeader(msg.get('MIME-Version', '')))
    headers['Subject'] = str(getMailHeader(msg.get('Subject', ''))) or 'EMPTY'
    headers['Content-Transfer-Encoding'] = str(getMailHeader(msg.get('Content-Transfer-Encoding', ''))) or 'EMPTY'
    headers['Content-Type'] = str(msg.get_content_type()) or 'EMPTY'
    headers['Charset'] = str(msg.get_content_charset('')) or 'EMPTY'
    headers['Received'] = str(msg.get_all('Received','EMPTY'))
    #Interesting header. Can be faked and pass badely configured gateway  https://isc.sans.edu/diary/UPS+Malware+Spam+Using+Fake+SPF+Headers/17693
    headers['Received-SPF'] = str(msg.get_all('Received-SPF','EMPTY'))
    headers['DKIM-Signature'] = str(msg.get('DKIM-Signature','EMPTY'))
    return headers

