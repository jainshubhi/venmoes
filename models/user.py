import uuid
from datetime import datetime


class User(object):
    '''
    first_name: First name of self. Will include middle name, initial or other
    parts of the name.
    last_name: Last name of self.
    email: Email that they use to sign up with Venmo/FB.
    username: Venmo username.
    is_user: Boolean whether this user uses this service, or is just a Venmo
    user.
    validated: Boolean whether this user has been validated or not. This means
    that they have the extraneous fields that can only be determined from a
    transaction.
    date_joined: Date the user joined Venmo.
    date_joined_ts: Date the user joined Venmo as UNIX timestamp.
    venmo_id: User ID assigned by Venmo.
    is_group: Boolean whether the Venmo username represents a group account.
    friends_count: Number of Venmo friends the user has.
    picture_url: URL to profile picture stored on Venmo.
    phone: Phone number associated with Venmo account.
    about: Description of user on Venmo account.
    fb_url: Facebook URL of self.
    '''
    def __init__(self, first_name, last_name, email, username, is_user,
                 validated=False, date_joined=None, venmo_id=None, id=None,
                 is_group=False, friends_count=0, picture_url=None, phone=None,
                 about=None):
        self.id             = id or self.get_id()
        self.first_name     = first_name
        self.last_name      = last_name
        self.email          = email
        self.username       = username
        self.is_user        = is_user
        self.validated      = validated
        self.date_joined    = self.dt(date_joined)
        self.date_joined_ts = int(datetime.strftime(self.date_joined, '%s')) if self.date_joined else None
        self.venmo_id       = venmo_id
        self.is_group       = is_group
        self.friends_count  = friends_count
        self.picture_url    = picture_url
        self.phone          = phone
        self.about          = None if about == ' ' else about
        self.fb_url         = self.get_fb_url(picture_url)

    def get_id(self):
        return str(uuid.uuid4())

    def dt(self, date):
        if isinstance(date, str):
            return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        elif isinstance(date, int):
            return datetime.utcfromtimestamp(date)

    def get_fb_url(self, picture_url):
        if picture_url and 'graph.facebook.com' in picture_url:
            # 2nd to last element is the id.
            fb_id = picture_url.split('/')[-2]
            return "https://facebook.com/{0}".format(fb_id)

    def dt_to_s(self):
        if self.date_joined:
            return datetime.strftime(self.date_joined, '%Y-%m-%dT%H:%M:%S')

    def __dict__(self, dynamo=True):
        d = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'username': self.username,
            'date_joined': self.date_joined_ts if dynamo else self.dt_to_s(),
            'venmo_id': self.venmo_id,
            'is_user': self.is_user,
            'validated': self.validated,
            'id': self.id,
            'is_group': self.is_group,
            'friends_count': self.friends_count,
            'profile_picture_url': self.picture_url,
            'fb_url': self.fb_url,
            'phone': self.phone,
            'about': self.about
        }
        return dict((k, v) for k, v in d.iteritems() if v is not None)
