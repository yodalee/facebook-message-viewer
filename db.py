class db():
    """Database abstraction class"""

    def __init__(self):
        self.db = self.createdb()

    def createdb(self):
        return None

    def insertUser(self, username):
        """create entry of user
        :username: username to be saved
        :content: raw content uploaded by user
        :return: userid of the inserted user
        """
        raise NotImplementedError

    def updateUser(self, userid):
        raise NotImplementedError

    def insertFriend(self, userid, fname, nickname):
        raise NotImplementedError

    def updateFriend(self, userid, fname, nickname):
        raise NotImplementedError

    def getFriend(self, userid):
        raise NotImplementedError

    def insertGroup(self, userid, gname):
        raise NotImplementedError

    def updateGroup(self, userid, gname, nickname):
        raise NotImplementedError

    def getGroup(self, userid):
        raise NotImplementedError

    def insertMessage(self, msgbuf):
        """insert list of message object into database
        :msgbuf: list of tuple that contain: (groupid, author, msgtime, text)
        """
        raise NotImplementedError

    def getMessage(self, userid, gname, startstr, endstr):
        raise NotImplementedError

    def getDate(self, userid, gname):
        raise NotImplementedError
