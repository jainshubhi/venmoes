import uuid

from datetime import datetime
from clients.dynamo_client import DynamoClient


class Transaction(object):
    '''
    date_created: Date the transaction was created.
    date_created_ts: date_created as string.
    payment_type: Can be one of "payment.created", "payment.requested"
    payment_status: 
    '''
    def __init__(self, data):
        dc = DynamoClient()
        self.date_created       = self.dt(data['data']['date_created'])
        self.date_created_ts    = data['data']['date_created']
        self.payment_type       = data['type']
        self.payment_status     = data['data']['status']
        self.date_completed     = self.dt(data['data']['date_completed'])
        self.date_completed_ts  = data['data']['date_completed']
        self.target_merchant    = data['data']['target']['merchant']
        self.redeemable_target  = data['data']['target']['redeemable_target']
        self.target_phone       = data['data']['target']['phone']
        self.target_type        = data['data']['target']['type']
        self.target             = dc.validate_user(data['data']['target'][self.target_type], validate=True)
        self.target_email       = data['data']['target']['email']
        self.actor              = dc.validate_user(data['data']['actor'], validate=True)
        self.audience           = data['data']['audience']
        self.note               = data['data']['note']
        self.amount             = data['data']['amount']
        self.action             = data['data']['action']
        self.date_authorized    = self.dt(data['data']['date_authorized'])
        self.date_authorized_ts = data['data']['date_authorized']
        self.date_reminded      = self.dt(data['data']['date_reminded'])
        self.date_reminded_ts   = data['data']['date_reminded']
        self.id                 = data['data']['id']

    def dt(self, date, ms=False):
        if isinstance(date, str):
            # Deal with microseconds
            if ms:
                return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
            return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        elif isinstance(date, int):
            return datetime.utcfromtimestamp(date)

    def __dict__(self):
        d = {
            'date_created': self.date_created_ts,
            'payment_type': self.payment_type,
            'payment_status': self.payment_status,
            'date_completed': self.date_completed_ts,
            'target_merchant': self.target_merchant,
            'redeemable_target': self.redeemable_target,
            'target_phone': self.target_phone,
            'target_type': self.target_type,
            'target': self.target.__dict__(dynamo=False),
            'target_email': self.target_email,
            'actor': self.actor.__dict__(dynamo=False),
            'audience': self.audience,
            'note': self.note,
            'amount': self.amount,
            'action': self.action,
            'date_authorized': self.date_authorized_ts,
            'date_reminded': self.date_reminded_ts,
            'id': self.id
        }
        return dict((k, v) for k, v in d.iteritems() if v is not None)
