import os
import mysql.connector


def linkStart():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "10.1.11.236"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "123qwe"),
        database=os.getenv("DB_NAME", "inspector"),
        port=int(os.getenv("DB_PORT", "5679")),
    )
    return connection


def getServerList():
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT servername, serveraddr FROM servers"
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    serverList = {}
    for server in results:
        serverList[server.get("servername")] = server.get("serveraddr")
    return serverList


def getAWSorNMGserverList():
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT servername, serveraddr FROM servers WHERE location LIKE '%aws%' OR location LIKE '%nmg%'"
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    serverList = []
    for server in results:
        serverList.append(server.get("servername"))
    return serverList


if __name__ == "__main__":
    print(getAWSorNMGserverList())
