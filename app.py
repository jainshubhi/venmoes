from flask import Flask, request

from clients.dynamo_client import DynamoClient
from clients.es_client import EsClient
from models.user import User
from models.transaction import Transaction

app = Flask(__name__)

@app.route('/user', methods=['POST'])
def new_user():
    '''
    Add new user.
    '''
    req_data = request.get_json()

    first_name = req_data.get('first_name')
    last_name  = req_data.get('last_name')
    email      = req_data.get('email')
    username   = req_data.get('venmo_username')
    # Need all valid values
    if first_name and last_name and email and username:
        user = User(first_name, last_name, email, username, True)
        dc = DynamoClient()
        if dc.add_user(user, new_account=True):
            return '200, ok.'
        else:
            return '422, user already exists.'
    else:
        return '400, invalid params.'

@app.route('/<user_id>', methods=['POST'])
def new_transaction(user_id):
    '''
    Add new transaction.
    '''
    # First check that the user is valid
    dc = DynamoClient()
    user = dc.get_user_by_id(user_id)
    if user is None:
        return '403, invalid auth.'

    # If user is valid, make sure that actor or target is the user.
    req_data = request.get_json()
    if req_data['data']['target'][req_data['data']['target']['type']]['username'] == user.username or req_data['data']['actor']['username'] == user.username:
        # Then, check the transaction
        try:
            t = Transaction(req_data)
        except:
            return '400, invalid payload.'
        # If all is good, index the transaction.
        es = EsClient()
        es.add_transaction(t)
        return '200, ok.'
    return '403, invalid auth.'

if __name__ == '__main__': 
    app.run()
