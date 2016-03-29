#!/usr/bin/python3.4
# _*_coding:Utf_8 _*

from elasticsearch_dsl import DocType, Index, String, Date, Integer, Boolean, Float
from elasticsearch_dsl.connections import connections
from elasticsearch.exceptions import ConnectionError

class Spam(DocType):
    X_Envelope_From = String()
    X_Envelope_To = String()
    X_Spam_Flag = Boolean()
    X_Spam_Score = Float()
    To = String()
    Date = Date()
    From = String()
    Reply_To = String()
    X_Priority = Integer()
    #X_Mailer = String()
    MIME_Version = Float()
    Content_Transfer_Encoding = String()
    Content_Type = String()
    Subject = String()
    #Message = String()

    class Meta:
        index = 'default_index'

    def save(self, ** kwargs):
        return super(Spam,self).save(** kwargs)


def indexMail(jsonMail, indexName, nodeIP, nodePort):
    
    # Try connecting to the Elasticsearch node
    try:
        connections.create_connection(hosts=[nodeIP+':'+str(nodePort)],timeout=3)
   
        # Create the mapping if the index doesn't exist
        if not Index(indexName).exists():
            Spam.init(index=indexName)
    
        # Create a new mail and initialize it
        newMail = Spam(X_Envelope_From=jsonMail['X-Envelope-From'])
        newMail.X_Envelope_To = jsonMail['X-Envelope-To']
        newMail.X_Spam_Flag = jsonMail['X-Spam-Flag']
        newMail.X_Spam_Score = jsonMail['X-Spam-Score']
        newMail.To = jsonMail['To']
        newMail.Date = jsonMail['Date']
        newMail.From = jsonMail['From']
        newMail.Reply_To = jsonMail['Reply-To']
        newMail.X_Priority = jsonMail['X-Priority']
        #newMail.X_Mailer = jsonMail['X-Mailer']
        newMail.MIME_Version = jsonMail['MIME-Version']
        newMail.Content_Transfer_Encoding = jsonMail['Content-Transfer-Encoding']
        newMail.Content_Type = jsonMail['Content-Type']
        newMail.Subject = jsonMail['Subject']
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
