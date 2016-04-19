#!/usr/bin/python3.4
# -*-coding:Utf-8 -*

import base64
import quopri

def decode_quote_printable_part(quo_pri_part):
    """
    Decodes a quote-printable encoded MIME object
    :param quo_pri_part: MIME msg part
    :return: decoded text, null if exception
    """
    try:
        return quopri.decodestring(quo_pri_part)
    except Exception as err:
        print("ERROR - Exception when decoding quoted printable: %s" % err)
        return str()

def decode_base64_part(base64_part):
    """
    Decodes base64 encoded MIME object
    :param base64_part: MIME msg part
    :return: decoded text, null if exception
    """
    try:
        return base64.b64decode(base64_part)
    except Exception as err:
        print("ERROR - Exception when decoding base64 part: %s" % err)
        return str()

