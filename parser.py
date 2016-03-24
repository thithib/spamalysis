import re
import email
import json
from email.utils import parseaddr
from email.header import decode_header

raw="""Return-Path: <>
Delivered-To: spam-quarantine
X-Envelope-From: <root@sd-29432.dedibox.fr>
X-Envelope-To: <bendeck@minet.net>
X-Envelope-To-Blocked: <bendeck@minet.net>
X-Quarantine-ID: <41qYbOJwNIvh>
X-Spam-Flag: YES
X-Spam-Score: 4.616
X-Spam-Level: ****
X-Spam-Status: Yes, score=4.616 tag=x tag2=1 kill=3 tests=[BAYES_00=-1.5,
	FREEMAIL_FORGED_FROMDOMAIN=0.001, FREEMAIL_FROM=0.001,
	HEADER_FROM_DIFFERENT_DOMAINS=0.001, HTML_MESSAGE=0.001,
	MIME_HTML_ONLY=1.199, RDNS_DYNAMIC=1.663, XPRIO=3.25]
	autolearn=no autolearn_force=no
Received: from mx2.minet.net ([192.168.102.26])
	by localhost (spam.minet.net [192.168.102.97]) (amavisd-new, port 10024)
	with ESMTP id 41qYbOJwNIvh for <bendeck@minet.net>;
	Wed, 16 Mar 2016 21:47:21 +0100 (CET)
Received-SPF: None (no SPF record) identity=mailfrom; client-ip=195.154.236.215; helo=sd-29432.dedibox.fr; envelope-from=root@sd-29432.dedibox.fr; receiver=bendeck@minet.net
Received: from sd-29432.dedibox.fr (195-154-236-215.rev.poneytelecom.eu [195.154.236.215])
	(using TLSv1 with cipher ADH-AES256-SHA (256/256 bits))
	(No client certificate requested)
	by mx2.minet.net (Postfix) with ESMTPS id 98E24B16BA5
	for <bendeck@minet.net>; Wed, 16 Mar 2016 21:47:21 +0100 (CET)
Received: by sd-29432.dedibox.fr (Postfix, from userid 0)
	id 864581E40479; Wed, 16 Mar 2016 21:06:21 +0100 (CET)
To: bendeck@minet.net
Subject: =?iso-8859-1?Q?Emballez_et_communiquez_avec_vos_sacs_=E9colo_personnalis?=  =?iso-8859-1?Q?=E9s_!?=
X-PHP-Originating-Script: 10000:class.phpmailer.php
Date: Wed, 16 Mar 2016 21:06:21 +0100
From: Carole - Teyssier Extimso <teyssier.extimso@orange.fr>
Reply-To: Carole - Teyssier Extimso <teyssier.extimso@orange.fr>
Message-ID: <7ef5c34de126c7de0db987fd8d1b5912@localhost.localdomain>
X-Priority: 3
X-Mailer: PHPMailer 5.2.4 (http://code.google.com/a/apache-extras.org/p/phpmailer/)
MIME-Version: 1.0
Content-Transfer-Encoding: 8bit
Content-Type: text/html; charset=iso-8859-1


La soci�t� Teyssier Extimso est pr�sente sur le march� de l�emballage depuis 1972.
<br>Notre soci�t� accompagne les entreprises de tous types : collectivit�s, industries, soci�t�s de services, commer�ants, dans la r�alisation et la fourniture de leurs emballages.
<br>Notre soci�t� conseille, usine ou fournit les emballages adapt�s � vos besoins.
<br>Interlocuteur unique et fabricant, notre savoir-faire est un gain de  temps pr�cieux pour vous.
<br>Notre r�putation s�est faite au cours des ann�es par nos engagements respect�s et appr�ci�s :
<br>- Qualit�
<br>- D�lais
<br>- Prix
<br>- Conseils
<br>Quel que soit vos besoins, n�h�sitez pas � nous consulter m�me si vous �tes � la recherche du mouton � cinq pattes.
<br>
<br>Bruno MOUTON
<br>Le G�rant.
<center>
<br>
<br>
Vous pouvez aussi visiter notre site web : <b><u>www.teyssier-extimso.fr</u></b> ou cliquer <b><a href="http://www.teyssier-extimso.fr" style="color:#000000;">ici</a></b><br />
<i>Pour une plus grande rapidit&eacute; de traitement nous vous invitons &agrave; nous r&eacute;pondre par mail ou directement sur notre site &agrave; la page contact</i><br /><br />
<p>Teyssier Extimso d'emballage plastique (S.A.R.L, n&deg; Siret 30226251400029)<br />
Zi Les Taillas - 43600 Ste SIGOLENE  / T&eacute;l : 04 71 66 63 80 / Fax : 04 71 66 64 25</p>
<p><font color="#858585">Pour vous d&eacute;sinscrire veuillez cliquer <a href="http://devis.teyssier-extimso.fr/desinscription.php?desinscription_t=8b0c0b286024f4a6d65e3353e4945e07162f2d63">ICI</a> ou bien r&eacute;pondre et inscrire d&eacute;sinscription dans le message avec le / les mail concern&eacute;s.</font></p>
</center>
</body>
</html>

"""



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

def parseMail(raw):
    """Parse the mail"""
    msg=email.message_from_string(raw)
    obj={'X-Envelope-From': purgeBrackets(getMailHeader(msg.get('X-Envelope-From',''))),
        'X-Envelope-To': purgeBrackets(getMailHeader(msg.get('X-Envelope-TO',''))),
        'X-Spam-Flag': getMailHeader(msg.get('X-Spam-Flag','')),
        'X-Spam-Score': float(getMailHeader(msg.get('X-Spam-Score',''))),
        'To': getMailHeader(msg.get('To','')),
        'Date': getMailHeader(msg.get('Date','')),
        'From': getMailHeader(msg.get('From','')),
        'Reply-to': getMailHeader(msg.get('Reply-to','')),
        'X-Priority': int(getMailHeader(msg.get('X-Priority',''))),
        'MIME-Version': float(getMailHeader(msg.get('MIME-Version',''))),
        'Subject': getMailHeader(msg.get('Subject','')),
        'Content-Transfer-Encoding': getMailHeader(msg.get('Content-Transfer-Encoding','')),
        'Content-Type': getMailHeader(msg.get('Content-Type',''))
        }
    return obj



print(parseMail(raw))
