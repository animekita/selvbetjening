import MySQLdb
from django.conf import settings
import md5

class VanillaForum:
    
    def __init__(self):
        self.db = MySQLdb.connect(host=settings.FORUM_DATABASE_HOST, 
                                  user=settings.FORUM_DATABASE_USER,
                                  passwd=settings.FORUM_DATABASE_PASSWORD,
                                  db=settings.FORUM_DATABASE_NAME)
    
    def userExists(self, username):
        cursor = self.db.cursor()
        cursor.execute("SELECT Name FROM LUM_User where Name=%s", (username,))
        result = cursor.fetchone()
        
        return (result != None)
    
    def createUser(self, Name, Password, Email, FirstName, LastName):
        """
        Password needs to be a MD5 has
        
        """
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO LUM_User (Name, Password, Email, FirstName, LastName) VALUES (%s, %s, %s, %s, %s)", (Name, Password, Email, FirstName, LastName))
        cursor.close()
    
    def changeUserEmail(self, username, email):
        cursor = self.db.cursor()
        cursor.execute("UPDATE LUM_User SET Email=%s WHERE Name=%s", (email, username))
        cursor.close()
    
    def changeUserPassword(self, username, password):
        passwd = md5.new(password)
        
        cursor = self.db.cursor()
        cursor.execute("UPDATE LUM_User SET Password=%s WHERE Name=%s", (passwd.hexdigest(), username))
        cursor.close()
    
    