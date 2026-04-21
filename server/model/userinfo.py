import mysql.connector
import json

class user(object):
    def __init__(self, username, domain):
        self.username = username
        self.domain = domain
def linkStart():
    connection = mysql.connector.connect(
        host='10.1.11.66',  # 数据库主机地址
        user='root',  # 数据库用户名
        password='123qwe',  # 数据库密码
        database='inspector',  # 数据库名称  
        port=8181  # 数据库端口
        # host='localhost',  # 数据库主机地址
        # user='root',  # 数据库用户名
        # password='123qwe',  # 数据库密码
        # database='inspector'  # 数据库名称
    )
    return connection

def premission(username, domain):
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    sql = f"SELECT isadmin FROM inspectoruser WHERE username='{username}' and domain='{domain}'"
    cursor.execute(sql)
    results = cursor.fetchall()
    if len(results) == 0:
        return False
    row = results[0]
    # 关闭游标和连接
    cursor.close()
    connection.close()
    if row.get("isadmin") == 1:
        return True
    else:
        return False

def getUserOwn(username, domain):
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    sql = f"SELECT userown FROM inspectoruser WHERE username='{username}' and domain='{domain}'"
    cursor.execute(sql)
    results = cursor.fetchall()
    # 打印结果
    cursor.close()
    connection.close()
    if len(results) == 0:
        return {}
    row = results[0]
    return json.loads(row.get("userown"))

def getUserList():
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT username, domain FROM inspectoruser"
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()# 关闭游标和连接
    connection.close()
    userList = {}
    for user in results:
        if user.get("domain") in userList:
            userList[user.get("domain")].append(user.get("username"))
        else:
            userList[user.get("domain")] = [user.get("username")]
    return userList

def getServerOwn(username, domain):
    userOwn = getUserOwn(username, domain)
    serverOwn = []
    for i in userOwn:
        serverOwn.append(i)
    return serverOwn

def setUserOwn(username, domain, userown):
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    sql = f"UPDATE inspectoruser SET userown='{json.dumps(userown)}' WHERE username='{username}' and domain='{domain}'"
    try:
        cursor.execute(sql)
        connection.commit()
    except Exception as e:
        print(e)
        cursor.close()# 关闭游标和连接
        connection.close()
        return False
    cursor.close()# 关闭游标和连接
    connection.close()
    return True
def addUser(username, domain):
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    sql = f"INSERT INTO inspectoruser(username, domain, isadmin) VALUES ('{username}', '{domain}', 0)"
    try:
        cursor.execute(sql)
        connection.commit()
    except Exception as e:
        print(e)
        cursor.close()# 关闭游标和连接
        connection.close()
        return False
    cursor.close()# 关闭游标和连接
    connection.close()
    return True

def deleteUser(username, domain):
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    sql = f"DELETE FROM inspectoruser WHERE username='{username}' and domain='{domain}'"
    try:
        cursor.execute(sql)
        connection.commit()
    except Exception as e:
        print(e)
        cursor.close()# 关闭游标和连接
        connection.close()
        return False
    cursor.close()# 关闭游标和连接
    connection.close()
    return True

def userToAdmin(username, domain):
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    sql = f"UPDATE inspectoruser SET isadmin=1 WHERE username='{username}' and domain='{domain}'"
    try:
        cursor.execute(sql)
        connection.commit()
    except Exception as e:
        print(e)
        cursor.close()# 关闭游标和连接
        connection.close()
        return False
    cursor.close()# 关闭游标和连接
    connection.close()
    return True

if __name__ == "__main__":
    print(getUserOwn("tanzhiying", "wequant"))