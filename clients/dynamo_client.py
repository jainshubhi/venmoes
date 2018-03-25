import boto3

from settings import *
from models.user import User
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.conditions import Key
from datetime import datetime


class DynamoClient(object):
    def __init__(self):
        dynamodb = boto3.resource('dynamodb', region_name=region_name,
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key)
        self.users = dynamodb.Table(users_table)

    def get_user_by_username(self, username):
        '''
        Return User by searching by Venmo username.
        '''
        response = self.users.query(
           IndexName='username-index',
           KeyConditionExpression=Key('username').eq(username)
        )
        if 'Items' not in response or len(response['Items']) == 0:
            return None
        dynamo_user = response['Items'][0]

        return self.to_user(dynamo_user)

    def get_user_by_email(self, email):
        '''
        Return User by searching by email.
        '''
        response = self.users.query(
           IndexName='email-index',
           KeyConditionExpression=Key('email').eq(email)
        )
        if 'Items' not in response or len(response['Items']) == 0:
            return None
        dynamo_user = response['Item'][0]

        return self.to_user(dynamo_user)

    def get_user_by_id(self, user_id):
        '''
        Return User by searching by their id.
        '''
        response = self.users.get_item(Key={'id': user_id})
        if 'Item' not in response:
            return None
        dynamo_user = response['Item']

        return self.to_user(dynamo_user)

    def to_user(self, dynamo_user):
        '''
        Convert a DynamoDB Representation of User to a User object.
        '''
        return User(
            dynamo_user.get('first_name'), dynamo_user.get('last_name'),
            dynamo_user.get('email'), dynamo_user.get('username'),
            dynamo_user.get('is_user'), id=dynamo_user.get('id'),
            validated=dynamo_user.get('validated'),
            date_joined=int(dynamo_user.get('date_joined')) if dynamo_user.get('date_joined') else None,
            venmo_id=dynamo_user.get('venmo_id'),
            is_group=dynamo_user.get('is_group'),
            friends_count=int(dynamo_user.get('friends_count')),
            picture_url=dynamo_user.get('picture_url'),
            phone=dynamo_user.get('phone'), about=dynamo_user.get('about')
        )

    def user_exists(self, email=None, username=None):
        '''
        Determine whether this user already exists or not.
        '''
        if email is None and username is None:
            return False
        if username:
            response = self.users.query(
               IndexName='username-index',
               KeyConditionExpression=Key('username').eq(username)
            )
            if 'Items' not in response or len(response['Items']) != 0:
                return True
        if email:
            response = self.users.query(
               IndexName='email-index',
               KeyConditionExpression=Key('email').eq(email)
            )
            if 'Items' not in response or len(response['Items']) != 0:
                return True
        return False

    def add_user(self, user, update=False, new_account=False):
        '''
        Add a User to to DynamoDB.
        '''
        if new_account:
            old_user = self.get_user_by_username(user.username) or self.get_user_by_email(user.email)
            if old_user:
                # If this user has an account with us already, return False
                if old_user.is_user:
                    return False
                # If this user is making a new account, we probably don't have their
                # email or phone. Also need to set is_user to True.
                old_user.email   = user.email
                old_user.phone   = user.phone or old_user.phone
                old_user.is_user = True
                user = old_user
        elif not self.user_exists(email=user.email, username=user.username) or update:
            pass
        else:
            return False
        data = user.__dict__()
        # Get rid of keys that have null values.
        data = dict((k, v) for k, v in data.iteritems() if v is not None)

        self.users.put_item(Item=data)
        return True

    def validate_user(self, data, validate=False):
        '''
        Add fields to a user that hasn't been validated yet.
        '''
        username = data['username']
        user     = self.get_user_by_username(username)
        # Case 1: user exists, and is already validated.
        if user:
            # Update email if it exists
            if data['email'] is not None:
                user.email = data['email']
            # Update phone if it exists
            if data['phone'] is not None:
                user.phone = data['phone']
            # Update friends_count if it exists
            if data['friends_count'] is not None:
                user.friends_count = data['friends_count']
            # Case 2: user exists, but is not validated yet.
            if not user.validated:
                user.validated = validate
                user.about = data['about']
                user.is_group = data['is_group']
                user.date_joined = user.dt(data['date_joined'])
                user.date_joined_ts = int(datetime.strftime(user.date_joined, '%s')) if user.date_joined else None
                user.venmo_id = data['id']
                user.picture_url = data['profile_picture_url']
                user.fb_url = user.get_fb_url(user.picture_url)
            self.add_user(user, update=True)
        # Case 3: This is a never-before seen user.
        else:
            user = User(
                data.get('first_name'), data.get('last_name'),
                data.get('email'), data.get('username'),
                False, validated=True, date_joined=data.get('date_joined'),
                venmo_id=data.get('id'),
                is_group=data.get('is_group'),
                friends_count=data.get('friends_count'),
                picture_url=data.get('profile_picture_url'),
                phone=data.get('phone'), about=data.get('about')
            )
            self.add_user(user)
        return user

    def remove_user(self, user_id):
        '''
        Remove User from DynamoDB.
        '''
        try:
            self.users.delete_item(Key={'id': user_id})
            return True
        except:
            return False
