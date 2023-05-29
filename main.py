from xmlrpc.client import ServerProxy
from nodeList import nodeList
import time
import prettytable as pt
import socket
import json
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)

class nodeConnector(object):   #服务器节点对象，一个对象就是一个Supervisord后端管理服务
    def __init__(self,name,address) -> None:
        self.name = name
        self.address = address
        self.connection = ServerProxy(address + "RPC2")
        self.state = self.connection.supervisor.getState()
        self.processList = self.connection.supervisor.getAllProcessInfo()
    

    def status(self):       #此节点Supervisor自身的状态
        print("-----------------------------------------------------------------------------")
        print(self.name,":",self.address,end=" | ")
        for i in self.state:
            print(i,": ",self.state[i],end=" | ")
        
        print("")
        print("------Process------")

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
      
        processListJson = json.dumps(tmp)
        print(self.__outputTable(tmp))
        print(processListJson)
        
        return processListJson

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
        except socket.timeout:
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

@app.route('/<serverName>/<processState>',methods=['GET'])
def processList(serverName,processState):
    print(Node)    
    # serverName = input("Which server you want to see? Input servername or all to see all server .\n")
    # processState = input("What kind of process do you want to see? Input running or stopped.\n")
    
    if serverName == "all":
        result=[]
        for i in Node:
            result.append([Node[i].status(),Node[i].listProcess(processState)])    
    elif serverName in nodeList:
        result = [Node[serverName].status(),Node[serverName].listProcess(processState)]                     
    else:
        result = "无法找到服务器"
    return json.dumps(result, ensure_ascii=False)
    

if __name__ == "__main__":
    socket.setdefaulttimeout(5) # 设置默认的超时时间为10秒
    link()
    app.run()