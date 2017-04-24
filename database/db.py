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

def insert():
    con = getConnection()
    try:
        with con.cursor() as cursor:
            sql = "insert into user (name,age) values (%s,%s)"
            cursor.execute(sql,('wangjin',12))
        con.commit()
    finally:
        con.close()
