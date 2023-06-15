#!/usr/bin/env python3

from User import readUser
from nodeLink import *
import json
from flask import Flask, jsonify, request, session
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class Config(object):
    SECRET_KEY = "WeQuant_WeQuant"
app.config.from_object(Config())
def init():
    global Node
    tmp1,tmp2,Node = link()
    return Node
@app.route('/serverList', methods=['GET']) #显示对应用户的服务器列表及连接测试状态
def serverList():
    print(request.args.get("userName"))
    nodeConnected,nodeConnectFailed = link(request.args.get("userName"))
    print(nodeConnected)
    servers={"ConnecctSucceed":nodeConnected,"ConnectFailled":nodeConnectFailed}
    response = jsonify(servers)
    return response

@app.route('/processList/all/',methods=['GET'])
def processList():
    result={}
    for i in Node:
        result[i]=Node[i].listProcess()
    return json.dumps(result, ensure_ascii=False)

@app.route('/log',methods=['GET'])
def processLog():
    hostName = request.args.get("servername")
    processName = request.args.get("processname")
    log=Node[hostName].connection.supervisor.tailProcessStdoutLog(processName,0,10000)
    print(log[0]) 
    content ={ "text":log[0]}
    return json.dumps(content, ensure_ascii=False)

@app.route('/start',methods=['GET'])
def startProcess():
    hostName = request.args.get("servername")
    processName = request.args.get("processname")
    Node[hostName].connection.supervisor.startProcess(processName)
    flag = {"flag":True}
    return json.dumps(flag, ensure_ascii=False)

@app.route('/stop',methods=['GET'])
def stopProcess():
    hostName = request.args.get("servername")
    processName = request.args.get("processname")
    Node[hostName].connection.supervisor.stopProcess(processName) 

@app.route('/login', methods=['POST'])
def login():
    users = readUser()
    data = request.get_json()
    print(data)
    try:
        enhancedPasswd=users[data.get('userName')]
    except:
        print("用户不存在")
    if data.get('userName') in users and data.get('password') == enhancedPasswd:
        return json.dumps({'flag': True})
    else:
        return json.dumps({'flag': False})

@app.route('/login/success', methods=['POST'])
def login_success():
    data = request.get_json()
    print(data["userToken"])
    session[data["userName"]] = data["userToken"]
    return json.dumps({'flag': True})

@app.route('/login/check', methods=['get'])
def login_check():
    print(session.get(request.cookies.get('userName')))
    if request.cookies.get('userToken') == session.get(request.cookies.get('userName')):
        print(request.cookies.get('userToken'))
        print("check")
        return json.dumps({'flag': True})
    else:
        print(request.cookies.get('userToken'))    
        print("no check")
        return json.dumps({'flag': False})

@app.route('/auth')
def auth():
    try:
        if request.cookies.get('userToken') == session[request.cookies.get('userName')]:
            return "",200
        else:
            return "",401
    except:
        return "",401
if __name__ == "__main__":  
    init()
    app.run()
