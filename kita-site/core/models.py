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
    
    def createUser(self, Name, Password, Email, FirstName, LastName, RoleID=3, StyleID=0):
        """
        Password needs to be a MD5 hash. The RoleID is set to 3, (member) by default. StyleID must be 0, otherwise a very ugly forum is shown ;D
        Dammit, there are to many "magic" values in this system...
        
        """
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO LUM_User (Name, Password, Email, FirstName, LastName, RoleID, StyleID) VALUES (%s, %s, %s, %s, %s, %s, %s)", (Name, Password, Email, FirstName, LastName, RoleID, StyleID))
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
    
    