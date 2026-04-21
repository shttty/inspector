import asyncio
from xmlrpc.client import ServerProxy, Fault
import xmlrpc.client
import model.serverinfo as serverinfo
import config

class AsyncNodeConnector:
    def __init__(self, name, address, timeout=10):
        self.name = name
        if config.user == "" or config.password is None:
            self.address = f"http://{address}/"
        else:
            self.address = f"http://{config.user}:{config.password}@{address}/"

        self.connection = ServerProxy(
            self.address + "RPC2",
            transport=TimeoutTransport(timeout=timeout)
        )
        self.state = None
        self.processList = None

    async def initialize(self):
        loop = asyncio.get_running_loop()
        self.state = await loop.run_in_executor(
            None, self.connection.supervisor.getState
        )
        self.processList = await loop.run_in_executor(
            None, self.connection.supervisor.getAllProcessInfo
        )

async def async_connect_to_node(servername, address, timeout=2):
    try:
        node = AsyncNodeConnector(servername, address, timeout)
        await node.initialize()
        print(f"{servername} {address} 连接成功")
        return (servername, node, True)
    except Exception as e:
        print(f"Error: {e}")
        print(f"{servername} {address} 无法连接")
        return (servername, None, False)

async def get_server_status(servers_list):
    return await asyncio.gather(*[
        async_connect_to_node(server, address) 
        for server, address in servers_list.items()
    ])

async def async_linkInit():
    server_list = serverinfo.getServerList()
    results = await get_server_status(server_list)

    link_succeeded = []
    link_failed = []
    nodes = {}

    for servername, node, success in results:
        if success:
            nodes[servername] = node
            link_succeeded.append(servername)
        else:
            link_failed.append(servername)

    return link_succeeded, link_failed, nodes

class TimeoutTransport(xmlrpc.client.Transport):
    def __init__(self, timeout=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn

def linkInit():
    link_succeeded, link_failed, nodes = asyncio.run(async_linkInit())
    return link_succeeded, link_failed, nodes

def link(servername):
    serverList = serverinfo.getServerList()
    try:
        address = serverList[servername]
        AsyncNodeConnector(servername, serverList[servername])
        return AsyncNodeConnector(servername, address)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    link_succeeded, link_failed, nodes = asyncio.run(async_linkInit())
    print(f"成功连接: {link_succeeded}")
    print(f"连接失败: {link_failed}")
    print(f"节点数量: {len(nodes)}")
