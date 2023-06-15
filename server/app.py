#!/usr/bin/env python3

from xmlrpc.client import ServerProxy
from nodeList import nodeList
import time
import prettytable as pt
import json
from flask import Flask, jsonify, request, session
import json
from userList import UserList
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

class Config(object):
    SECRET_KEY = "WeQuant_WeQuant"
app.config.from_object(Config())


class nodeConnector(object):   #服务器节点对象，一个对象就是一个Supervisord后端管理服务
    def __init__(self,name,address) -> None:
        self.name = name
        self.address = f"http://{address}/"
        self.connection = ServerProxy(self.address + "RPC2")
        self.state = self.connection.supervisor.getState()
        self.processList = self.connection.supervisor.getAllProcessInfo()

    def status(self):       #此节点Supervisor自身的状态
        print("-----------------------------------------------------------------------------")
        print(self.name,":",self.address,end=" | ")
        for i in self.state:
            print(i,": ",self.state[i],end=" | ")
        
        print("")
        print("------Process------")
        return self.state
    def __outputTable(self,tmp):  #在终端中以表格形式输出数据
        table = pt.PrettyTable(['name',
                                'group',
                                'start',
                                'stop',
                                'now',       
                                'state',
                                'statename',
                                'spawnerr',
                                'exitstatus',
                                'pid',
                                'description'])

        for info in tmp:
            start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(info["start"])))
            stop = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(info["stop"])))
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(info["now"])))
            
            table.add_row([info['name'],
                            info['group'],
                            start,
                            stop,
                            now,
                            info['state'],
                            info['statename'],
                            info['spawnerr'],
                            info['exitstatus'],
                            info['pid'],
                            info['description']])
        return table

    def listProcess(self):  #按照需求列出此节点Supervisor受管的进程及其状态
        tmp = self.processList[:]
        print(self.__outputTable(tmp))
        return tmp

def link():  #用于连接测试及初始化每个节点的对象，必须至少运行一次以获取Supervisor方法

    linkSuccessed = []
    linkFiailed = [] 
    global Node 
    Node = {}
    for hostName, address in nodeList.items():
        try:   
            Node[hostName] = nodeConnector(hostName, address)
            print(hostName, address, "连接成功")
            linkSuccessed.append(hostName)
        except:
            print(hostName, address, "无法连接")
            linkFiailed.append(hostName)  
    return linkSuccessed,linkFiailed

@app.route('/serverList', methods=['GET']) #显示服务器列表及连接测试状态
def serverList():
    nodeConnected,nodeConnectFailed = link()
    servers={"AllNodes":nodeList,"ConnecctSucceed":nodeConnected,"ConnectFailled":nodeConnectFailed}
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
    data = request.get_json()
    print(data)
    try:
        enhancedPasswd=UserList[data.get('userName')]
    except:
        print("用户不存在")
    if data.get('userName') in UserList and data.get('password') == enhancedPasswd:
        return json.dumps({'flag': True})
    else:
        return json.dumps({'flag': False})

@app.route('/login/success', methods=['POST'])
def login_success():
    data = request.get_json()
    print(data["userToken"])
    session[data['userName']] = data["userToken"]
    return json.dumps({'flag': True})

@app.route('/login/check', methods=['get'])
def login_check():
    if request.cookies.get('userToken') == session[request.cookies.get('userName')]:
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
    link()
    app.run()
