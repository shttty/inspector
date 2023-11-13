import model.userinfo as userinfo

def processShowPremissionControl(plist, username, domain, servername):
    if userinfo.premission(username=username, domain=domain):
        return plist
    allow = userinfo.getUserOwn(username=username, domain=domain) #获取用户拥有的服务器：服务字典
    if servername not in allow:
        return False
    processList = []
    for programe in plist:
        if programe.get("name") == programe.get("group"):
            programeName = programe.get("name")
        else:
            programeName = f"{programe.get('group')}:{programe.get('name')}"
        if  programeName in allow.get(servername):
            processList.append(programe)
    return processList

def processXPremissionControl(servername, processname, username, domain):
    
    if userinfo.premission(username=username, domain=domain):
        return True
    allow = userinfo.getUserOwn(username=username, domain=domain)
    try:    
        if processname in allow.get(servername):
            return True
    except:
            return False
    return False