from config.configHelper import getConfig
import pymysql.cursors


host = getConfig("db","host")
user = getConfig("db","user")
password = getConfig("db","password")
db = getConfig("db","db")
charset = getConfig("db","charset")

def getConnection():
    return pymysql.connect(host = host,
                            user = user,
                            password = password,
                            db = db,
                            charset = charset,
                            cursorclass=pymysql.cursors.DictCursor)

def insert(gmetadata,con):
    with con.cursor() as cursor:
        sql = "insert into eromanga (gid,token,archiver_key,title,title_jpn,category,thumb,uploader,posted,filecount,filesize,expunged,rating,torrentcount,tags) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        for data in gmetadata:
            cursor.execute(sql,(data['gid'],data['token'],data['archiver_key'],data['title'],data['title_jpn'],data['category'],data['thumb'],data['uploader'],int(data['posted']),int(data['filecount']),int(data['filesize']),data['expunged'],data['rating'],int(data['torrentcount']),str(data['tags'])))
    con.commit()

def select():
    try:
        con = getConnection()
        with con.cursor() as cursor:
            sql = "select * from eromanga"
            cursor.execute(sql)
            res = cursor.fetchall()
            for r in res:
                print(r)
    finally:
        con.close()
    