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

    def status(self):
        """
        打印此 Supervisor 节点的状态。

        返回值:
        dict: 包含此 Supervisor 节点当前状态的字典。
        """
        # 打印分隔线
        print("-" * 66)
        # 打印节点名称和地址
        print(f"{self.name}: {self.address}", end=" | ")
        # 打印 Supervisor 节点的状态
        for i in self.state:
            print(f"{i}: {self.state[i]}", end=" | ")
        # 打印换行符
        print("")
        # 打印进程分隔线
        print("------Process------")
        # 返回此 Supervisor 节点当前状态
        return self.state

    
    def __outputTable(self,tmp):  #在终端中以表格形式输出数据
        """
        在终端中以表格形式输出数据。

        参数：
        - data: 包含要显示数据的字典列表。

        返回值：
        - 包含格式化数据的 PrettyTable, 直接print就好    
        """
        table = pt.PrettyTable(['name',     # 创建一个 PrettyTable 对象，并指定列名
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

        for info in tmp:                    # 循环遍历数据，根据列名格式化数据
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

def link(user="admin") :
    """
    该函数用于连接服务器列表中的每个节点并初始化它们的对象。
    必须至少运行一次以获取 Supervisor 方法。

    参数:
        user (str): 用于连接服务器的用户。默认为 "admin"。

    返回:
        Tuple[List[str], List[str], Dict[str, Any]]: 包含成功连接的节点主机名列表、
        失败连接的列表和包含节点对象的字典的元组。
    """
    with open("server_list/server_list.json",'r') as f: # 从json配置文件读取服务器列表
        nodeList=json.load(f)
    
    linkSuccessed = []
    linkFiailed = [] 
    Node = {}
    for hostName, address in nodeList.items():
        # 未开用户检验时没有cookie就是None,开放所有资源，开用户登陆校验时会有cookie则根据用户拥有的服务器池进行选择性发送数据
        if serversOfUser(user) == None or (serversOfUser(user) == "all") or (address in serversOfUser(user)):
            try:
                Node[hostName] = nodeConnector(hostName, address)
                print(hostName, address, "连接成功")
                linkSuccessed.append(hostName)
            except:
                print(hostName, address, "无法连接")
                linkFiailed.append(hostName)
    return linkSuccessed,linkFiailed,Node

def list(nodeName):
    with open("server_list/server_list.json",'r') as f: # 从json配置文件读取服务器列表
        nodeList=json.load(f)
    connect=ServerProxy(f"http://{nodeList[nodeName]}/RPC2")
    return connect.supervisor.getAllProcessInfo()

