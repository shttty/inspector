from ldap3 import NTLM, Server, Connection

def userAuth(domain, username, password, server=None ):
    loginname=f"{domain}\\{username}"
    developer="wequant"
    research="strategy"
    developerAD="10.1.2.5"
    researchAD="10.1.6.3"
    if server==None:
        if domain == developer:
            server=Server(developerAD)
            print("developerGroup")
        elif domain == research:
            server=Server(researchAD)
            print("researchGroup")
    else:
        server=Server(server)
        print("ouherGroup")
    print(loginname, password)
    connection = Connection(server, user=loginname, password=password, authentication=NTLM)
    # 连接到AD域控制服务器
    try:
        if not connection.bind():
            print(f'{loginname}用户名或密码错误')
            return False
        else:
            print(f'{loginname}用户验证成功')
            connection.unbind()
            return True
    except Exception as e:
        print(e)
        print(f'{loginname}用户名或密码错误')
        return False
# if __name__=="__main__":
#     print(userAuth())