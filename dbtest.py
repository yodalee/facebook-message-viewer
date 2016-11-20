import sqlite3
import unittest

class REdictParseTest(unittest.TestCase):
    def testdbUser(self):
        db = sqlite3.connect("user.db")
        file = open("README.md", 'r')
        file_content = file.read()

        query = "INSERT INTO dbUser (file, isReady) VALUES (?, 0)"
        db.execute(query, [sqlite3.Binary(file_content)])
        db.commit()

        c = db.cursor()
        c.execute("SELECT file FROM dbUser")
        data = c.fetchone()
        file = data[0]

        db.execute("DELETE FROM dbUser WHERE id > -1")
        db.commit()
        db.close()


if __name__ == "__main__":
    unittest.main()
