import mysql.connector

def linkStart():
    connection = mysql.connector.connect(
        # host='localhost',  # 数据库主机地址
        # user='root',  # 数据库用户名
        # password='123qwe',  # 数据库密码
        # database='inspector'  # 数据库名称
        host='10.1.11.66',  # 数据库主机地址
        user='root',  # 数据库用户名
        password='123qwe',  # 数据库密码
        database='inspector',  # 数据库名称  
        port=8181  # 数据库端口
    )
    return connection

def getServerList():
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT servername, serveraddr FROM servers"
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()# 关闭游标和连接
    connection.close()
    serverList = {}
    for server in results:
        serverList[server.get("servername")]= server.get("serveraddr")
    return serverList

if __name__ == "__main__":
    print(getServerList())
