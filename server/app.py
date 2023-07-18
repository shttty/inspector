#!/usr/bin/env python3

import os
from User import readUser
from nodeLink import *
import json
from flask import Flask, jsonify, request, session
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class Config(object):
    SECRET_KEY = "WeQuant_WeQuant"
app.config.from_object(Config())


@app.route('/serverList', methods=['GET']) #显示对应用户的服务器列表及连接测试状态
def serverList():
    print("username:",request.cookies.get("userName"))
    nodeConnected,nodeConnectFailed,_ = link(request.cookies.get("userName")) #获得用户连接的服务器列表及服务器状态
    print(nodeConnected,"connected",nodeConnectFailed,"failed")
    servers={"ConnecctSucceed":nodeConnected,"ConnectFailled":nodeConnectFailed}
    response = jsonify(servers)
    return response

@app.route('/processList/all/',methods=['GET'])
def processList():
    _,_,Node = link(request.cookies.get("userName"))
    result={}
    for i in Node:
        result[i]=Node[i].listProcess()
    return json.dumps(result, ensure_ascii=False)

@app.route('/log',methods=['GET']) #获取某个服务器的某个进程的stdout日志，暂时没有获取stderr日志的功能
def processLog():
    _,_,Node = link(request.cookies.get("userName"))
    hostName = request.args.get("servername")
    processName = request.args.get("processname")
    log=Node[hostName].connection.supervisor.tailProcessStdoutLog(processName,0,10000) #日志最大10000个字符，计划以后由用户指定，
    content ={ "text":log[0]}
    print("Send log.") 
    return json.dumps(content, ensure_ascii=False)

@app.route('/start',methods=['GET'])  #启动一个进程
def startProcess():
    _,_,Node = link(request.cookies.get("userName"))
    hostName = request.args.get("servername")
    processName = request.args.get("processname")
    Node[hostName].connection.supervisor.startProcess(processName)
    flag = {"flag":True}
    return json.dumps(flag, ensure_ascii=False)

@app.route('/stop',methods=['GET']) #停止一个进程
def stopProcess():
    _,_,Node = link(request.cookies.get("userName"))
    hostName = request.args.get("servername")
    processName = request.args.get("processname")
    Node[hostName].connection.supervisor.stopProcess(processName) 
    return json.dumps({'flag':True}, ensure_ascii=False)

@app.route('/login', methods=['POST']) #登录模块，用于用户权限控制
def login():
    """
    用于用户验证的登录端点。

    从文件中读取用户数据，获取请求中的JSON数据，并检查提供的用户名和密码是否与数据库中的任何用户匹配。

    返回：
        包含布尔值的“flag”键的JSON对象，指示登录尝试的成功或失败。
    """

    users = readUser()  # 从文件读取用户数据
    data = request.get_json()  # 获取请求中的JSON数据
    print(data)
    try:
        enhancedPasswd = users[data.get('userName')]
    except:
        print("用户不存在")
    if data.get('userName') in users and data.get('password') == enhancedPasswd:
        return json.dumps({'flag': True})  # 登录成功
    else:
        return json.dumps({'flag': False})  # 登录失败

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
        print("Checked")
        return json.dumps({'flag': True})
    else:
        print(request.cookies.get('userToken'))    
        print("Check failed")
        return json.dumps({'flag': False})

@app.route('/auth') 
def auth():
    """
    用户控制模块，启用nginx中的用户控制后除登录请求外其他所有的请求都会被拦截，
    并重定向至auth进行验证，如果未登录则重定向至登录页面。
    """
    try: #检查是否有cookie
        if request.cookies.get('userToken') == session[request.cookies.get('userName')]:
            return "",200 #用户已登录
        else:
            return "",401 #用户无权限
    except:
        return "",401 #cookie/session为空
    
@app.route('/logout')
def logout():
    session.pop(request.cookies.get('userName'))
    return "",200
##############################临时措施
@app.route('/getFiles', methods=['GET']) #从服务器拷贝文件夹
def getFiles():
    os.system('/usr/bin/bash /root/inspector/getFile_S.sh')
###############################
@app.route('/tree', methods=['GET'])
def outputTree():
    hostName = request.args.get("server")
    _,_,Node = link(request.cookies.get("userName"))
    progress = request.args.get("progress")
    print(hostName)
    print(progress)
    #return "ok"
    path=os.path.dirname(os.path.dirname(Node[hostName].connection.supervisor.getProcessInfo(progress).get("stdout_logfile")))
    print(path)
    result = json.dumps(Node[hostName].connection.inspector_files.tree(path), ensure_ascii=False)
    return result

@app.route('/download', methods=['POST'])
def download():
    path = request.json.get("path")
    hostName = request.json.get("server")
    _,_,Node = link(request.cookies.get("userName"))
    print(path)
    print(request.cookies.get("userName"))
    result = json.dumps(Node[hostName].connection.inspector_files.rsync(path, request.cookies.get("userName")), ensure_ascii=False)
    return result
if __name__ == "__main__":
    app.run(debug=True,port=5000)