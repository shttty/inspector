from xmlrpc.client import ServerProxy
import model.serverinfo as serverinfo

class nodeConnector(object):   #服务器节点对象，一个对象就是一个Supervisord后端管理服务
    def __init__(self,name,address) -> None:
        self.name = name
        self.address = f"http://{address}/"
        self.connection = ServerProxy(self.address + "RPC2")
        self.state = self.connection.supervisor.getState()
        self.processList = self.connection.supervisor.getAllProcessInfo()


def linkInit() :
    """
    该函数用于连接服务器列表中的每个节点并初始化它们的对象。
    必须至少运行一次以获取 Supervisor 方法。

    参数:
        user (str): 用于连接服务器的用户。默认为 "admin"。

    返回:
        Tuple[List[str], List[str], Dict[str, Any]]: 包含成功连接的节点主机名列表、
        失败连接的列表和包含节点对象的字典的元组。
    """
    global serverList 
    serverList = serverinfo.getServerList()
    linkSuccessed = []
    linkFiailed = [] 
    Nodes = {}
    for servername, address in serverList.items():
        # 未开用户检验时没有cookie就是None,开放所有资源，开用户登陆校验时会有cookie则根据用户拥有的服务器池进行选择性发送数据
        try:
            Nodes[servername] = nodeConnector(servername, address)
            print(servername, address, "连接成功")
            linkSuccessed.append(servername)
        except Exception as e:
            print(e)
            print(servername, address, "无法连接")
            linkFiailed.append(servername)
    return linkSuccessed,linkFiailed,Nodes

def link(servername):
    address = serverList[servername]
    return nodeConnector(servername,address)


def list(servername):
    connect=ServerProxy(f"http://{serverList[servername]}/RPC2")
    return connect.supervisor.getAllProcessInfo()

def linkTest(servername, serveraddr):
    try:
        nodeConnector(servername, serveraddr)
        return True
    except:
        return False

