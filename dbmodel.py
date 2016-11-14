from google.appengine.ext import ndb

# Basic datastruct in user blob
class dbUser(ndb.Model):
    user = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()
    isReady = ndb.BooleanProperty()


class dbGroup(ndb.Model):
    user_key = ndb.KeyProperty(kind=dbUser, required=True)
    group = ndb.StringProperty()


class dbMessage(ndb.Model):
    group_key = ndb.KeyProperty(kind=dbGroup, required=True)
    author = ndb.StringProperty()
    time = ndb.DateTimeProperty()
    content = ndb.TextProperty()
