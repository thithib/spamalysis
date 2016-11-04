#!/usr/bin/python3.4
# _*_coding:Utf_8 _*

from elasticsearch_dsl import DocType, Index, String, Date, Integer, Boolean, Float, Object, GeoPoint
from elasticsearch_dsl.connections import connections
from elasticsearch.exceptions import ConnectionError
from analyzers import emailAnalyzer, fetchReceived, headerSanitizer,emailAnalyzerReceived,getDate
class Spam(DocType):
    X_Envelope_From = Object(
            properties = {
                'email': String(index='not_analyzed'),
                'header': String(index='not_analyzed'),
                'localpart': String(index='not_analyzed'),
                'domain': String(index='not_analyzed'),
                'location': GeoPoint(),
                'domain_type': String(index='not_analyzed'),
                'country_code' : String(index='not_analyzed')
                }
    )
    X_Envelope_To = String(index='not_analyzed')
    X_Spam_Flag = Boolean()
    X_Spam_Score = Float()
    To = String(multi=True, index='not_analyzed')
    Date = Date()
    From = String(index='not_analyzed')
    Reply_To = String(index='not_analyzed')
    X_Priority = Integer()
    #X_Mailer = String()
    MIME_Version = String(index='not_analyzed')
    Subject = String()
    Content_Transfer_Encoding = String(index='not_analyzed')
    Content_Type = String(index='not_analyzed')
    Charset = String(index='not_analyzed')
    Received = String(index='not_analyzed')
    Hops = Integer()
    Received_SPF = String(index = 'not_analyzed')
    DKIM_Signature = String(index = 'not_analyzed')
    ##### HEADERS RAJOUTES SUITE A TRAITEMENT ####
    spfResult = String(index = 'not_analyzed')
    spfTrue = String(index = 'not_analyzed')
    DKIM_Result = String(index = 'not_analyzed')
    DKIM_KeyLength = Integer()
    #############################################
    #Message = String()
    phoneNumbers = String(multi=True, index='not_analyzed')
    URLs = String(multi=True, index='not_analyzed')
    attachmentsTypes = String(multi=True, index='not_analyzed')
    attachmentsSizes = Integer(multi=True)

    class Meta:
        index = 'default_index'
        doc_type = 'spam'

    def save(self, ** kwargs):
        return super().save(** kwargs)


def indexMail(jsonMail, indexName, nodeIP, nodePort, database):
    # Try connecting to the Elasticsearch node
    try:
        connections.create_connection(hosts=[nodeIP+':'+str(nodePort)],timeout=3)

        # Create the mapping if the index doesn't exist
        if not Index(indexName).exists():
            Spam.init(index=indexName)

        # Create a new mail and initialize it
        if (jsonMail['X-Envelope-To'] != "EMPTY"):
            newMail = Spam(X_Envelope_To=jsonMail['X-Envelope-To'])
        if (jsonMail['X-Envelope-From'] != "EMPTY" and jsonMail['X-Envelope-From'] != "<>" and jsonMail['X-Envelope-From'] != 'False'):
            newMail.X_Envelope_From.header = jsonMail['X-Envelope-From']
            analyzingResult = emailAnalyzer(jsonMail['X-Envelope-From'], database)
            newMail.X_Envelope_From.email = analyzingResult[0]
            newMail.X_Envelope_From.localpart = analyzingResult[1]
            newMail.X_Envelope_From.domain = analyzingResult[2]
            newMail.X_Envelope_From.domain_type = analyzingResult[4]
            if (analyzingResult[3] != ""):
                newMail.X_Envelope_From.location = analyzingResult[3]
            if (analyzingResult[5] != ""):
                newMail.X_Envelope_From.country_code = analyzingResult[5]
        if (jsonMail['X-Spam-Flag'] != "EMPTY"):
            newMail.X_Spam_Flag = jsonMail['X-Spam-Flag']
        if (jsonMail['To'] != "EMPTY"):
            for mail in headerSanitizer(jsonMail['To']):
                newMail.To.append(mail)
        if (jsonMail['From'] != "EMPTY"):
            newMail.From = jsonMail['From']
        if (jsonMail['Reply-To'] != "EMPTY"):
            newMail.Reply_To = jsonMail['Reply-To']
        if (jsonMail['Content-Transfer-Encoding'] != "EMPTY"):
            newMail.Content_Transfer_Encoding = jsonMail['Content-Transfer-Encoding']
        if (jsonMail['Content-Type'] != "EMPTY"):
            newMail.Content_Type = jsonMail['Content-Type']
        if (jsonMail['Subject'] != "EMPTY") :
            newMail.Subject = jsonMail['Subject']
        if (jsonMail['Charset'] != "EMPTY") :
            newMail.Charset = jsonMail['Charset']
        if (jsonMail['Received'] != "EMPTY") :
            newMail.Received = jsonMail['Received']
            newMail.Hops = len(fetchReceived(jsonMail['Received']))
            if(jsonMail['X-Envelope-From'] == 'EMPTY' or jsonMail['X-Envelope-From'] == '<>' or jsonMail['X-Envelope-From'] == 'False'):
                analyzingResult = emailAnalyzerReceived(jsonMail['Received'], database)
                newMail.X_Envelope_From.domain = analyzingResult[0]
                newMail.X_Envelope_From.domain_type = analyzingResult[2]
                if (analyzingResult[1] != ""):
                    newMail.X_Envelope_From.location = analyzingResult[1]
        if (jsonMail.get('Received-SPF','EMPTY') != "EMPTY") :
            newMail.Received_SPF = jsonMail['Received-SPF']
            if (jsonMail.get('spfResult','EMPTY') != 'EMPTY'):
                newMail.spfResult = jsonMail['spfResult']
            if(jsonMail.get('spfTrue','EMPTY') != 'EMPTY'):
                newMail.spfTrue = jsonMail['spfTrue']
        if (jsonMail['DKIM-Signature'] != "EMPTY") :
            newMail.DKIM_Signature = jsonMail['DKIM-Signature']
            newMail.DKIM_Result = jsonMail['dkimResult']
            if jsonMail['dkimResult'] == 'DKIM OK' and jsonMail.get('dkimKey','EMPTY') != 'EMPTY':
                newMail.DKIM_KeyLength = jsonMail['dkimKey']
        newMail.X_Spam_Score = jsonMail['X-Spam-Score']
        if(jsonMail['Date'] != '' and jsonMail['Date'] != 'EMPTY'):
            newMail.Date = jsonMail['Date']
        else:
            if (getDate(jsonMail['Received']) !='EMPTY'):
                newMail.Date = getDate(jsonMail['Received'])
        newMail.X_Priority = jsonMail['X-Priority']
        newMail.MIME_Version = jsonMail['MIME-Version']
        for phoneNumber in jsonMail['phoneNumbers'] :
            newMail.phoneNumbers.append(phoneNumber)
        for url in jsonMail['URLs'] :
            newMail.URLs.append(url)
        for attachmentType in jsonMail['attachmentsTypes']:
            newMail.attachmentsTypes.append(attachmentType)
        for attachmentSize in jsonMail['attachmentsSizes']:
            newMail.attachmentsSizes.append(attachmentSize)
        #newMail.X_Mailer = jsonMail['X-Mailer']
        #newMail.Message = jsonMail['Message']

        # Overwrite the index name for the new mail
        newMail.meta.index = indexName
        # Save index
        result = newMail.save()
        # Close connection to Elasticsearh node
        connections.remove_connection('default')
        return result

    except ConnectionError:
        return False
