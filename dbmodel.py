from google.appengine.ext import ndb

# Basic datastruct in user blob
class UserMessage(ndb.Model):
    user = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()
    isReady = ndb.BooleanProperty()
