from config.configHelper import getConfig
import pymysql.cursors
import time


host = getConfig("db","host")
user = getConfig("db","user")
password = getConfig("db","password")
db = getConfig("db","db")
charset = getConfig("db","charset")

class db:

    connection = pymysql.connect(host = host,
                                user = user,
                                password = password,
                                db = db,
                                charset = charset,
                                cursorclass=pymysql.cursors.DictCursor)                 

    def getConnection(self):
        return pymysql.connect(host = host,
                                user = user,
                                password = password,
                                db = db,
                                charset = charset,
                                cursorclass=pymysql.cursors.DictCursor)

    def insertEromanga(self,data):
        with self.connection.cursor() as cursor:
            sql = "insert into eromanga (gid,token,archiver_key,title,title_jpn,category,thumb,uploader,posted,filecount,filesize,expunged,rating,torrentcount,tags) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(data['gid'],data['token'],data['archiver_key'],data['title'],data['title_jpn'],data['category'],data['thumb'],data['uploader'],int(data['posted']),int(data['filecount']),int(data['filesize']),data['expunged'],data['rating'],int(data['torrentcount']),str(data['tags'])))
        self.connection.commit()

    def insertEroimage(self,images):
        with self.connection.cursor() as cursor:
            sql = "insert into eroimage (gid,token,sequence,url) values (%s,%s,%s,%s)"
            for image in images:
                cursor.execute(sql,(image['gid'],image['token'],image['sequence'],image['url']))
        self.connection.commit()

    def insertThumbimage(self,image):
        with self.connection.cursor() as cursor:
            sql = "insert into thumbimage (gid,token,sequence,url) values (%s,%s,%s,%s)"
            cursor.execute(sql,(image['gid'],image['token'],image['sequence'],image['url']))
        self.connection.commit() 

    def getLastPosted(self):
        with self.connection.cursor() as cursor:
            sql = "select min(posted) as lastposted from eromanga"
            cursor.execute(sql)
            res = cursor.fetchone()
            if res['lastposted'] == None:
                return int(time.time())
            return int(res['lastposted'])
    