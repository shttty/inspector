#!/usr/bin/env python3

import nodeLink
import json
from flask import Flask, jsonify, request, session
import inspectorEncrypt as ien
import msADauth
import permissioncontrol
import model.userinfo as userinfo
import model.serverinfo as serverinfo
import time
import hashlib

app = Flask(__name__)
app.secret_key = 'WeQuant'


@app.route('/serverList', methods=['GET']) #显示对应用户的服务器列表及连接测试状态
def serverList():
    global nodeConnected
    nodeConnected,nodeConnectFailed,_ = nodeLink.linkInit()
    print(nodeConnected,"connected",nodeConnectFailed,"failed")
    servers={"ConnecctSucceed":nodeConnected,"ConnectFailled":nodeConnectFailed}
    response = jsonify(servers)
    return response

@app.route('/processList',methods=['GET'])
def processList():
    serverName = request.args.get("servername") #获取某个服务器的进程列表
    node = nodeLink.link(serverName)
    plist = node.connection.supervisor.getAllProcessInfo()
    return json.dumps(plist, ensure_ascii=False)

@app.route('/premissionTest',methods=['GET'])
def premissionTest():
    if userinfo.premission(username=session.get("username"), domain=session.get("domain")):
        return  json.dumps({"flag":True}, ensure_ascii=False)
    else:
        return json.dumps({"flag":False}, ensure_ascii=False)

@app.route('/processListInServerOwn',methods=['GET'])
def processListInServerOwn():
    serverName = request.args.get("servername") #获取某个服务器的进程列表
    node = nodeLink.link(serverName)
    plist = node.connection.supervisor.getAllProcessInfo()
    plistInControl = permissioncontrol.processShowPremissionControl(plist,session.get("username"),session.get("domain"),serverName)
    return json.dumps(plistInControl, ensure_ascii=False)

@app.route('/userOwn',methods=['GET'])
def userOwn():
    username = request.args.get("username")
    domain = request.args.get("domain")
    print(session.get("username"),session.get("domain"))
    if userinfo.premission(username=session.get("username"), domain=session.get("domain")) or (username == session.get("username") and domain == session.get("domain")):
        return  json.dumps(userinfo.getUserOwn(username=username, domain=domain), ensure_ascii=False)
    else:
        return "",401

@app.route('/serverOwn',methods=['GET'])
def serverOwn():
    if userinfo.premission(username=session.get("username"), domain=session.get("domain")):
        return  json.dumps(nodeConnected, ensure_ascii=False)
    userOwnServer = userinfo.getServerOwn(session.get("username"), session.get("domain"))
    userOwnServerConnected = list(filter(lambda x: x in userOwnServer, nodeConnected))
    return json.dumps(userOwnServerConnected, ensure_ascii=False)

@app.route('/userList',methods=['GET'])
def userList():
    return json.dumps(userinfo.getUserList(), ensure_ascii=False)

@app.route('/log',methods=['GET']) #获取某个服务器的某个进程的stdout日志，暂时没有获取stderr日志的功能
def processLog():
    serverName = request.args.get("servername")
    node = nodeLink.link(serverName)
    processName = request.args.get("processname")
    log=node.connection.supervisor.tailProcessStdoutLog(processName,0,10000) #日志最大10000个字符，计划以后由用户指定，
    content ={ "text":log[0]}
    print("Send log.")
    return json.dumps(content, ensure_ascii=False)

@app.route('/start',methods=['GET'])  #启动一个进程
def startProcess():
    servername = request.args.get("servername")
    node = nodeLink.link(servername)
    processname = request.args.get("processname")
    flag = {"flag": False}
    if permissioncontrol.processXPremissionControl(servername, processname, session.get("username"), session.get("domain")):
        try:
            if node.connection.supervisor.startProcess(processname):
                flag["flag"] = True
        except  Exception as e:
            print(e)
    return json.dumps(flag, ensure_ascii=False)

@app.route('/stop', methods=['GET'])
def stopProcess():
    servername = request.args.get("servername")
    node = nodeLink.link(servername)
    processname = request.args.get("processname")
    flag = {"flag": False}
    if permissioncontrol.processXPremissionControl(servername, processname, session.get("username"), session.get("domain")):
        try:
            if node.connection.supervisor.stopProcess(processname):
                flag["flag"] = True
        except Exception as e:
            print(e)
    return json.dumps(flag, ensure_ascii=False)
    
@app.route('/logout')
def logout():
    session.clear()
    return "",200

@app.route('/loginstate', methods=['get'])
def loginstate():
    if session.get("username") == None or session.get("domain") == None:
        keyword = f"{time.time()**2}"
        md5_hash = hashlib.md5(keyword.encode('utf-8')).hexdigest()
        session["key"] = md5_hash
        return json.dumps({"flag": False,"key": md5_hash}, ensure_ascii=False)
    res = {"flag": True, "username": session.get("username"), "domain": session.get("domain")}
    return json.dumps(res, ensure_ascii=False)
    

@app.route('/login', methods=['POST'])
def login():
    domain = request.json.get("domain")
    username = request.json.get("username")
    password = request.json.get("password")
    print(domain, username, password) 
    key = session.get("key")
    print(key)
    try:
        passwd = ien.aesDecrypt(password, key)
        print(passwd)
    except:
        return json.dumps({"flag": False}, ensure_ascii=False)
    session.pop("key", None)
    if msADauth.userAuth(domain, username, passwd):
        data = {"flag": True}
        session["username"] = username
        session["domain"] = domain
        print("login")
        return json.dumps(data, ensure_ascii=False)
    else:
        return json.dumps({'flag': False}, ensure_ascii=False)

@app.route('/tree', methods=['GET'])
def outputTree():
    nodeLink.linkInit()
    servername = request.args.get("server")
    node = nodeLink.link(servername)
    processname = request.args.get("process")
    print(servername,processname)
    if permissioncontrol.processXPremissionControl(servername, processname, session.get("username"), session.get("domain")):
        try:
            result = {"tree": json.dumps(node.connection.inspector.tree(processname), ensure_ascii=False)}
        except Exception as e:
            print(e)
            result = {"flag": False}
    return json.dumps(result, ensure_ascii=False)
    
@app.route('/download', methods=['POST'])
def download():
    nodeLink.linkInit()
    username = f"{session.get('username')}@{session.get('domain')}"
    path = request.json.get("path")
    processname = request.json.get("process")
    servername = request.json.get("server")
    node = nodeLink.link(servername)
    if permissioncontrol.processXPremissionControl(servername, processname, session.get("username"), session.get("domain")):
        try:
            result = json.dumps(node.connection.inspector.download(path, processname, username), ensure_ascii=False)
        except Exception as e:
            print(e)
            result = {"flag": False}
    return json.dumps(result, ensure_ascii=False)

@app.route('/dest')
def dest():
    username = f"{session.get('username')}@{session.get('domain')}"
    servername = request.args.get("server")
    node = nodeLink.link(servername)
    result ={"dest": node.connection.inspector.getDest(username)}
    return json.dumps(result, ensure_ascii=False)

@app.route('/details', methods=['GET'])
def details():
    serverName = request.args.get("servername")
    process = request.args.get("processname")
    print(serverName,process)
    node = nodeLink.link(serverName)
    result = json.dumps(node.connection.inspector.details(process), ensure_ascii=False)
    return result

@app.route('/setUserOwn', methods=['POST'])
def setUserOwn():
    if userinfo.premission(username=session.get("username"), domain=session.get("domain")) == False:
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    username = request.args.get("username")
    domain = request.args.get("domain")
    userown = request.json.get("userown")
    print(userown)
    if userinfo.setUserOwn(username=username, domain=domain, userown=userown):
        print("set")
        return json.dumps({"flag": True}, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)

@app.route('/addUser', methods=['GET'])
def addUser():
    if userinfo.premission(username=session.get("username"), domain=session.get("domain")) == False:
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    username = request.args.get("username")
    domain = request.args.get("domain")
    if userinfo.addUser(username=username, domain=domain):
        print("add")
        return json.dumps({"flag": True}, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)
    
@app.route('/deleteUser', methods=['GET'])
def deleteUse():
    if userinfo.premission(username=session.get("username"), domain=session.get("domain")) == False:
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    username = request.args.get("username")
    domain = request.args.get("domain")
    if userinfo.deleteUser(username=username, domain=domain):
        print("del")
        return json.dumps({"flag": True}, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)

@app.route('/userToAdmin')
def userToAdmin():
    if userinfo.premission(username=session.get("username"), domain=session.get("domain")) == False:
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    username = request.args.get("username")
    domain = request.args.get("domain")
    if userinfo.userToAdmin(username=username, domain=domain):
        print("userToAdmin")
        return json.dumps({"flag": True}, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)

@app.route('/addServer')
def addServer():
    if userinfo.premission(username=session.get("username"), domain=session.get("domain")) == False:
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    servername = request.args.get("servername")
    serverAddress = request.args.get("ip")
    if servername in serverinfo.getServerList():
        return json.dumps({"flag": False}, ensure_ascii=False)
    if nodeLink.linkTest(servername, serverAddress):
        serverinfo.addServer(servername, serverAddress)
        print(f"server {servername} {serverAddress} is added")
        return json.dumps({"flag": True}, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)
    
if __name__ == "__main__":
    app.run(port=5000)