class db():
    """Database abstraction class"""

    def __init__(self):
        self.db = self.createdb()

    def createdb(self):
        return None

    def getUpload(self, userid):
        raise NotImplementedError

    def updateUser(self, userid):
        raise NotImplementedError

    def insertUser(self, content):
        """create entry of user

        :content: raw content uploaded by user
        :return: userid of the inserted id

        """
        raise NotImplementedError

    def insertGroup(self, userid, groupname):
        raise NotImplementedError

    def insertMessage(self, msgbuf):
        """insert array of message object into database

        :msgbuf: array of tuple that contain: (groupid, author, msgtime, text)
        """
        raise NotImplementedError

    def getGroup(self, userid):
        raise NotImplementedError

    def getUser(self, groupname, startstr, endstr):
        raise NotImplementedError
