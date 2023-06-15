
import json
from xmlrpc.client import ServerProxy
import time
import prettytable as pt
from User import serversOfUser

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

def link(user="admin"):  #用于连接测试及初始化每个节点的对象，必须至少运行一次以获取Supervisor方法
    with open("server_list/server_list.json",'r') as f:
        nodeList=json.load(f)
    linkSuccessed = []
    linkFiailed = [] 
    global Node 
    Node = {}
    for hostName, address in nodeList.items():
        if address in serversOfUser(user) or serversOfUser(user) == "all":
            try:    
                Node[hostName] = nodeConnector(hostName, address)
                print(hostName, address, "连接成功")
                linkSuccessed.append(hostName)
            except:
                print(hostName, address, "无法连接")
                linkFiailed.append(hostName)  
    return linkSuccessed,linkFiailed,Node