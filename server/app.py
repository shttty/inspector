from xmlrpc.client import ServerProxy
from nodeList import nodeList
import time
import prettytable as pt
import socket
import json
from flask import Flask, jsonify, request, Response
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
cors = CORS(app)

class nodeConnector(object):   #服务器节点对象，一个对象就是一个Supervisord后端管理服务
    def __init__(self,name,address) -> None:
        self.name = name
        self.address = "http://" + address + "/"
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
        return ;

    def listProcess(self,state="all"):   #按照需求列出此节点Supervisor受管的进程及其状态
        tmp = self.processList[:]
        if state == "running":
            for process in self.processList:
                if process['state'] != 10 and process['state'] !=  20:
                    tmp.remove(process) 
        elif state == "stopped":
            for process in self.processList:
                if process['state'] == 20 or process['state'] == 10:
                    tmp.remove(process)

        elif state == "all":
            pass
      
        # processListJson = json.dumps(tmp)
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
@cross_origin()
def serverList():
    nodeConnected,nodeConnectFailed = link()
    servers={"AllNodes":nodeList,"ConnecctSucceed":nodeConnected,"ConnectFailled":nodeConnectFailed}
    response = jsonify(servers)
    return response

@app.route('/processList/all/',methods=['GET'])
@cross_origin()
def processList():
    # serverName = input("Which server you want to see? Input servername or all to see all server .\n")
    # processState = input("What kind of process do you want to see? Input running or stopped.\n")
    result={}
    for i in Node:
        result[i]=Node[i].listProcess("all")
    return json.dumps(result, ensure_ascii=False)

@app.route('/log',methods=['GET'])
@cross_origin()
def processLog():
        # 获取前端传递的代理目标 URL，例如 https://example.com/
    hostName = request.args.get("servername")
    processName = request.args.get("processname")
    log=Node[hostName].connection.supervisor.tailProcessStdoutLog(processName,0,10000) 
    content = "<pre>"+log[0]+"</pre>"
    print(content)
    return content

@app.route('/start',methods=['GET'])
@cross_origin()
def startProcess():
    hostName = request.args.get("servername")
    processName = request.args.get("processname")
    flag =  Node[hostName].connection.supervisor.startProcess(processName)
    if flag:
        return "True"
    else:
        return "False"
@app.route('/restart',methods=['GET'])
@cross_origin()
def restartProcess():
    hostName = request.args.get("servername")
    processName = request.args.get("processname")
    flag = Node[hostName].connection.supervisor.stopProcess(processName)
    if flag:
        return "True"
    else:
        return "Fales"
@app.route('/stop',methods=['GET'])
@cross_origin()
def stopProcess():
    hostName = request.args.get("servername")
    processName = request.args.get("processname")
    flag = Node[hostName].connection.supervisor.stopProcess(processName)
    if flag:
        return "True"
    else:
        return "Fales"
  

@app.route('/login',methods=['POST'])
def login():
    pass

if __name__ == "__main__":
    socket.setdefaulttimeout(5) # 设置默认的超时时间为10秒
    link()
    app.run()
