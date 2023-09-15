from xmlrpc.client import ServerProxy


server = ServerProxy('http://localhost:9001/RPC2')
def tree():
    #processPath = os.path.dirname(server.supervisor.getProcessInfo(name).get("stdout_logfile"))
    #return server.inspector_files.tree(processPath)
    return server.inspector_files.tree("/home/sunheng/dev/tree")
def download(path):
    return server.inspector_files.rsync(path)