from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from settings import *
from models.transaction import Transaction


class EsClient(object):
    def __init__(self):
        # awsauth = AWS4Auth(aws_access_key_id, aws_secret_access_key, region_name, 'es')

        self.client = Elasticsearch([es_host])

    def add_transaction(self, transaction):
        '''
        Index Transaction to Elasticsearch.
        '''
        body = transaction.__dict__()

        self.client.index(index=es_index, body=body, doc_type=es_index, id=body['id'])
