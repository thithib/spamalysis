#!/usr/bin/python3.4
# -*-coding:Utf-8 -*

import os
import re

from bs4 import BeautifulSoup


def processBody(mailBody, mailHeaders):
    """Search for some interesting content"""
    resultBody = dict()
    resultBody['phoneNumbers'] = processPhoneNumbers(mailBody)
    resultBody['URLs'] = processURLs(mailBody)
    return resultBody

def processPhoneNumbers(mailBody):
    """Get phone numbers from e-mail body"""
    phoneNumbers = list()
    r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    for part, html in mailBody:
        for x in r.findall(str(part)):
            phoneNumbers.append(x)
    return list(set(phoneNumbers))

def processURLs(mailBody):
    """Get URLs from e-mail body"""
    URLs = list()
    for content, isHtml in mailBody:
        if isHtml:
            URLs.extend(getURLsFromHtml(str(content)))
        else:
            URLs.extend(getURLsFromPlain(str(content)))
    return list(set(URLs))

def getURLsFromHtml(html_code):
    """
    Parses the given HTML text and extracts the href links from it.
    The input should already be decoded
    :param html_code: Decoded html text
    :return: A list of URLs, a null list if exception
    """
    try:
        soup = BeautifulSoup(html_code, "html.parser")
        html_urls = []
        for link in soup.findAll("a"):
            url = link.get("href")
            if url and "http" in url:
                html_urls.append(url)
        return html_urls
    except Exception as err:
        print("ERROR - Exception when parsing the html body: %s" % err)
        return []

def getURLsFromPlain(email_data):
    """
    Parses the given plain text and extracts the URLs out of it
    :param email_data: plain text to parse
    :return: A list of URLs, a null list if exception
    """
    try:
        pattern = "abcdefghijklmnopqrstuvwxyz0123456789./\~#%&()_-+=;?:[]!$*,@'^`<{|\""
        indices = [m.start() for m in re.finditer('http://', email_data)]
        indices.extend([n.start() for n in re.finditer('https://', email_data)])
        urls = []
        if indices:
            if len(indices) > 1:
                new_lst = zip(indices, indices[1:])
                for x, y in new_lst:
                    tmp = email_data[x:y]
                    url = ""
                    for ch in tmp:
                        if ch.lower() in pattern:
                            url += ch
                        else:
                            break
                    urls.append(url)
            tmp = email_data[indices[-1]:]
            url = ""
            for ch in tmp:
                    if ch.lower() in pattern:
                        url += ch
                    else:
                        break
            urls.append(url)
            return urls
        return []

    except Exception as err:
        print("ERROR - Exception when parsing plain text for urls: %s" % err)
        return []

def processAttachments(attachments):
    """
    Conducts a basic study of e-mail attachments
    :param attachments: list of attachments as tuples (name, content)
    """
    resultAttachments = dict()
    for name, content in attachments:
        filename = '/tmp/' + name
        with open(filename, 'wb') as f:
            f.write(content)
        # Do things on the file and add results to resultAttachments dict
        os.remove(filename)
    return resultAttachments

