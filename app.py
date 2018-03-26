from flask import Flask, request, Response

from clients.dynamo_client import DynamoClient
from clients.es_client import EsClient
from models.user import User
from models.transaction import Transaction

import json

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
            return Response(json.dumps({'200 OK': 'The request has succeeded'}),
                            status=200, mimetype='application/json')
        else:
            return Response(json.dumps({'422 BAD': 'The user already exists'}),
                            status=422, mimetype='application/json')
    else:
        return Response(json.dumps({'400 BAD': 'Invalid params for adding user'}),
                        status=400, mimetype='application/json')

@app.route('/<user_id>', methods=['POST'])
def new_transaction(user_id):
    '''
    Add new transaction.
    '''
    # First check that the user is valid
    dc = DynamoClient()
    user = dc.get_user_by_id(user_id)
    if user is None:
        return Response(json.dumps({'403 BAD': 'Unauthorized access to webhook'}),
                        status=403, mimetype='application/json')

    # If user is valid, make sure that actor or target is the user.
    req_data = request.get_json()
    if req_data['data']['target'][req_data['data']['target']['type']]['username'] == user.username or req_data['data']['actor']['username'] == user.username:
        # Then, check the transaction
        try:
            t = Transaction(req_data)
        except:
            return Response(json.dumps({'400 BAD': 'Invalid params for transaction payload'}),
                            status=400, mimetype='application/json')
        # If all is good, index the transaction.
        es = EsClient()
        es.add_transaction(t)
        return Response(json.dumps({'200 OK': 'The request has succeeded'}),
                        status=200, mimetype='application/json')
    return Response(json.dumps({'403 BAD': 'Unauthorized access to webhook'}),
                    status=403, mimetype='application/json')

if __name__ == '__main__': 
    app.run()
