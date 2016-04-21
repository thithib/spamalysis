#!/usr/bin/python3.4
# _*_coding:Utf_8 _*

from elasticsearch_dsl import DocType, Index, String, Date, Integer, Boolean, Float, Object, GeoPoint
from elasticsearch_dsl.connections import connections
from elasticsearch.exceptions import ConnectionError
from analyzers import emailAnalyzer

class Spam(DocType):
    X_Envelope_From = Object(
            properties = {
                'email': 'string',
                'header': 'string',
                'localpart': 'string',
                'domain': 'string',
                'location': 'geo_point'
                }
    )
    X_Envelope_To = String()
    X_Spam_Flag = Boolean()
    X_Spam_Score = Float()
    To = String()
    Date = Date()
    From = String()
    Reply_To = String()
    X_Priority = Integer()
    #X_Mailer = String()
    MIME_Version = String()
    Content_Transfer_Encoding = String()
    Content_Type = String()
    Subject = String()
    #Message = String()

    class Meta:
        index = 'default_index'
        doc_type = 'spam'

    def save(self, ** kwargs):
        return super().save(** kwargs)


def indexMail(jsonMail, indexName, nodeIP, nodePort):

    # Try connecting to the Elasticsearch node
    try:
        connections.create_connection(hosts=[nodeIP+':'+str(nodePort)],timeout=3)

        # Create the mapping if the index doesn't exist
        if not Index(indexName).exists():
            Spam.init(index=indexName)

        # Create a new mail and initialize it
        if (jsonMail['X-Envelope-To'] != "EMPTY"):
            newMail = Spam(X_Envelope_To=jsonMail['X-Envelope-To'])
        if (jsonMail['X-Envelope-From'] != "EMPTY" and jsonMail['X-Envelope-From'] != "<>"):
            newMail.X_Envelope_From.header = jsonMail['X-Envelope-From']
            analyzingResult = emailAnalyzer(jsonMail['X-Envelope-From'])
            newMail.X_Envelope_From.email = analyzingResult[0]
            newMail.X_Envelope_From.localpart = analyzingResult[1]
            newMail.X_Envelope_From.domain = analyzingResult[2]
            if (analyzingResult[3] != ""):
                newMail.X_Envelope_From.location = analyzingResult[3]
        if (jsonMail['X-Spam-Flag'] != "EMPTY"):
            newMail.X_Spam_Flag = jsonMail['X-Spam-Flag']
        if (jsonMail['To'] != "EMPTY"):
            newMail.To = jsonMail['To']
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
        newMail.X_Spam_Score = jsonMail['X-Spam-Score']
        newMail.Date = jsonMail['Date']
        newMail.X_Priority = jsonMail['X-Priority']
        newMail.MIME_Version = jsonMail['MIME-Version']
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
