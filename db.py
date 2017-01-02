class db():
    """Database abstraction class"""

    def __init__(self):
        self.db = self.createdb()

    def createdb(self):
        return None

    def insertUser(self, username, content):
        """create entry of user

        :content: raw content uploaded by user
        :username: username to be saved
        :return: userid of the inserted id

        """
        raise NotImplementedError

    def getUpload(self, userid):
        raise NotImplementedError

    def getUserByName(self, username):
        raise NotImplementedError

    def updateUser(self, userid):
        raise NotImplementedError

    def insertGroup(self, userid, groupname):
        raise NotImplementedError

    def getGroup(self, userid):
        raise NotImplementedError

    def insertMessage(self, msgbuf):
        """insert array of message object into database

        :msgbuf: array of tuple that contain: (groupid, author, msgtime, text)
        """
        raise NotImplementedError

    def getMessage(self, groupname, startstr, endstr):
        raise NotImplementedError
