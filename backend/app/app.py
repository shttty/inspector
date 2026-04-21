import os
import node_link as nodeLink
import json
from xmlrpc.client import Fault
from flask import Flask, current_app, jsonify, request, session
import encrypt as ien
import auth as msADauth
import permission as permissioncontrol
import model.userinfo as userinfo
import model.serverinfo as serverinfo
import model.ldapinfo as ldapinfo
import time
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "WeQuant")

# Ensure ldap_servers table exists and load merged config on startup
ldapinfo.ensureTable()
msADauth.load_config()


def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip


@app.route("/serverList", methods=["GET"])  # 显示对应用户的服务器列表及连接测试状态
def serverList():
    global nodeConnected
    nodeConnected, nodeConnectFailed, _ = nodeLink.linkInit()
    print(nodeConnected, "connected", nodeConnectFailed, "failed")
    servers = {"ConnecctSucceed": nodeConnected, "ConnectFailled": nodeConnectFailed}
    response = jsonify(servers)
    return response


@app.route("/processList", methods=["GET"])
def processList():
    try:
        serverName = request.args.get("servername")
        if not serverName:
            app.logger.warning("No server name provided")
            return jsonify({"error": "Server name is required"}), 400

        node = nodeLink.link(serverName)
        if node is None:
            app.logger.error(f"Failed to connect to server: {serverName}")
            return jsonify({"error": f"Failed to connect to server: {serverName}"}), 500

        try:
            plist = node.connection.supervisor.getAllProcessInfo()
        except Fault as e:
            app.logger.error(
                f"XML-RPC Fault for {serverName}: {e.faultCode} - {e.faultString}"
            )
            return jsonify({"error": f"XML-RPC Fault: {e.faultString}"}), 500
        except Exception as e:
            app.logger.error(f"Error getting process list for {serverName}: {str(e)}")
            return jsonify({"error": f"Error getting process list: {str(e)}"}), 500

        return json.dumps(plist, ensure_ascii=False)

    except Exception as e:
        app.logger.error(f"Unexpected error in processList: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/premissionTest", methods=["GET"])
def premissionTest():
    if userinfo.premission(
        username=session.get("username"), domain=session.get("domain")
    ):
        return json.dumps({"flag": True}, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)


@app.route("/processListInServerOwn", methods=["GET"])
def processListInServerOwn():
    serverName = request.args.get("servername")  # 获取某个服务器的进程列表
    node = nodeLink.link(serverName)
    plist = node.connection.supervisor.getAllProcessInfo()
    plistInControl = permissioncontrol.processShowPremissionControl(
        plist, session.get("username"), session.get("domain"), serverName
    )
    return json.dumps(plistInControl, ensure_ascii=False)


@app.route("/userOwn", methods=["GET"])
def userOwn():
    username = request.args.get("username")
    domain = request.args.get("domain")
    print(session.get("username"), session.get("domain"))
    if userinfo.premission(
        username=session.get("username"), domain=session.get("domain")
    ) or (username == session.get("username") and domain == session.get("domain")):
        return json.dumps(
            userinfo.getUserOwn(username=username, domain=domain), ensure_ascii=False
        )
    else:
        return "", 401


@app.route("/serverOwn", methods=["GET"])
def serverOwn():
    if userinfo.premission(
        username=session.get("username"), domain=session.get("domain")
    ):
        return json.dumps(nodeConnected, ensure_ascii=False)
    if userinfo.onDuty(session.get("username"), session.get("domain")):
        dutyServer = list(
            set(nodeConnected) & set((serverinfo.getAWSorNMGserverList()))
        )
        return json.dumps(dutyServer, ensure_ascii=False)
    userOwnServer = userinfo.getServerOwn(
        session.get("username"), session.get("domain")
    )
    userOwnServerConnected = list(filter(lambda x: x in userOwnServer, nodeConnected))
    return json.dumps(userOwnServerConnected, ensure_ascii=False)


@app.route("/userList", methods=["GET"])
def userList():
    return json.dumps(userinfo.getUserList(), ensure_ascii=False)


@app.route(
    "/log", methods=["GET"]
)  # 获取某个服务器的某个进程的stdout日志，暂时没有获取stderr日志的功能
def processLog():
    serverName = request.args.get("servername")
    node = nodeLink.link(serverName)
    processName = request.args.get("processname")
    log = node.connection.supervisor.tailProcessStdoutLog(
        processName, 0, 10000
    )  # 日志最大10000个字符，计划以后由用户指定，
    content = {"text": log[0]}
    print("Send log.")
    return json.dumps(content, ensure_ascii=False)


@app.route("/start", methods=["GET"])  # 启动一个进程
def startProcess():
    servername = request.args.get("servername")
    node = nodeLink.link(servername)
    processname = request.args.get("processname")
    flag = {"flag": False}
    if permissioncontrol.processXPremissionControl(
        servername, processname, session.get("username"), session.get("domain")
    ):
        try:
            if node.connection.supervisor.startProcess(processname):
                flag["flag"] = True
        except Exception as e:
            print(e)
    return json.dumps(flag, ensure_ascii=False)


@app.route("/stop", methods=["GET"])
def stopProcess():
    servername = request.args.get("servername")
    node = nodeLink.link(servername)
    processname = request.args.get("processname")
    flag = {"flag": False}
    if permissioncontrol.processXPremissionControl(
        servername, processname, session.get("username"), session.get("domain")
    ):
        try:
            if node.connection.supervisor.stopProcess(processname):
                flag["flag"] = True
        except Exception as e:
            print(e)
    return json.dumps(flag, ensure_ascii=False)


@app.route("/logout")
def logout():
    session.clear()
    return "", 200


@app.route("/loginstate", methods=["get"])
def loginstate():
    if session.get("username") is None or session.get("domain") is None:
        keyword = f"{time.time() ** 2}"
        md5_hash = hashlib.md5(keyword.encode("utf-8")).hexdigest()
        session["key"] = md5_hash
        return json.dumps({"flag": False, "key": md5_hash}, ensure_ascii=False)
    res = {
        "flag": True,
        "username": session.get("username"),
        "domain": session.get("domain"),
    }
    return json.dumps(res, ensure_ascii=False)


@app.route("/login", methods=["POST"])
def login():
    domain = request.json.get("domain")
    username = request.json.get("username")
    password = request.json.get("password")
    print(domain, username, password)
    key = session.get("key")
    print(key)
    try:
        passwd = ien.aesDecrypt(password, key)
        # print(passwd)
    except Exception as e:
        print(e)
        return json.dumps({"flag": False}, ensure_ascii=False)
    session.pop("key", None)
    user_info = msADauth.userAuth(domain, username, passwd)
    if user_info:
        data = {"flag": True}
        session["username"] = username
        session["domain"] = domain
        session["role"] = user_info.get("role", "user")
        session["display_name"] = user_info.get("display_name", username)
        print("login")
        return json.dumps(data, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)


@app.route("/tree", methods=["GET"])
def outputTree():
    nodeLink.linkInit()
    servername = request.args.get("server")
    node = nodeLink.link(servername)
    processname = request.args.get("process")
    print(servername, processname)
    if permissioncontrol.processXPremissionControl(
        servername, processname, session.get("username"), session.get("domain")
    ):
        try:
            result = {
                "tree": json.dumps(
                    node.connection.inspector.tree(processname), ensure_ascii=False
                )
            }
        except Exception as e:
            print(e)
            result = {"flag": False}
    return json.dumps(result, ensure_ascii=False)


@app.route("/dest")
def dest():
    username = f"{session.get('username')}@{session.get('domain')}"
    servername = request.args.get("server")
    node = nodeLink.link(servername)
    result = {"dest": node.connection.inspector.getDest(username)}
    return json.dumps(result, ensure_ascii=False)


@app.route("/details", methods=["GET"])
def details():
    ip = get_client_ip()
    current_app.logger.info(f"Request from IP: {ip}")
    serverName = request.args.get("servername")
    process = request.args.get("processname")
    print(serverName, process)
    try:
        node = nodeLink.link(serverName)
        result = json.dumps(
            node.connection.inspector.details(process), ensure_ascii=False
        )
        return result
    except Exception as e:
        print(e)
        return "", 404


@app.route("/setUserOwn", methods=["POST"])
def setUserOwn():
    if (
        userinfo.premission(
            username=session.get("username"), domain=session.get("domain")
        )
        is False
    ):
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    username = request.args.get("username")
    domain = request.args.get("domain")
    userown = request.json.get("userown")
    print(userown)
    if userinfo.setUserOwn(username=username, domain=domain, userown=userown):
        print("set")
        return json.dumps({"flag": True}, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)


@app.route("/addUser", methods=["GET"])
def addUser():
    if (
        userinfo.premission(
            username=session.get("username"), domain=session.get("domain")
        )
        is False
    ):
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    username = request.args.get("username")
    domain = request.args.get("domain")
    if userinfo.addUser(username=username, domain=domain):
        print("add")
        return json.dumps({"flag": True}, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)


@app.route("/deleteUser", methods=["GET"])
def deleteUse():
    if (
        userinfo.premission(
            username=session.get("username"), domain=session.get("domain")
        )
        is False
    ):
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    username = request.args.get("username")
    domain = request.args.get("domain")
    if userinfo.deleteUser(username=username, domain=domain):
        print("del")
        return json.dumps({"flag": True}, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)


@app.route("/userToAdmin")
def userToAdmin():
    if (
        userinfo.premission(
            username=session.get("username"), domain=session.get("domain")
        )
        is False
    ):
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    username = request.args.get("username")
    domain = request.args.get("domain")
    if userinfo.userToAdmin(username=username, domain=domain):
        print("userToAdmin")
        return json.dumps({"flag": True}, ensure_ascii=False)
    else:
        return json.dumps({"flag": False}, ensure_ascii=False)

@app.route("/ldap/users", methods=["GET"])
def ldapUsers():
    if not userinfo.premission(
        username=session.get("username"), domain=session.get("domain")
    ):
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    domain = request.args.get("domain", "")
    query = request.args.get("q", "*")
    users = msADauth.search_users(domain, query)
    return json.dumps(users, ensure_ascii=False)


# ---------------------------------------------------------------------------
# LDAP server config CRUD (admin only)
# ---------------------------------------------------------------------------

def _require_admin():
    if not userinfo.premission(
        username=session.get("username"), domain=session.get("domain")
    ):
        return json.dumps({"flag": False}, ensure_ascii=False), 401
    return None


@app.route("/ldap/servers", methods=["GET"])
def ldapServerList():
    denied = _require_admin()
    if denied:
        return denied
    servers = ldapinfo.getLdapServers()
    # Mask bind_password in response
    for srv in servers:
        if srv.get("bind_password"):
            srv["bind_password"] = "******"
    return json.dumps(servers, ensure_ascii=False, default=str)


@app.route("/ldap/servers/<name>", methods=["GET"])
def ldapServerGet(name):
    denied = _require_admin()
    if denied:
        return denied
    srv = ldapinfo.getLdapServer(name)
    if not srv:
        return json.dumps({"flag": False, "error": "not found"}, ensure_ascii=False), 404
    if srv.get("bind_password"):
        srv["bind_password"] = "******"
    return json.dumps(srv, ensure_ascii=False, default=str)


@app.route("/ldap/servers", methods=["POST"])
def ldapServerAdd():
    denied = _require_admin()
    if denied:
        return denied
    data = request.json
    if not data or not data.get("name") or not data.get("host"):
        return json.dumps({"flag": False, "error": "name and host required"}, ensure_ascii=False), 400
    ok = ldapinfo.addLdapServer(data)
    if ok:
        msADauth.reload_config()
    return json.dumps({"flag": ok}, ensure_ascii=False)


@app.route("/ldap/servers/<name>", methods=["PUT"])
def ldapServerUpdate(name):
    denied = _require_admin()
    if denied:
        return denied
    data = request.json
    if not data:
        return json.dumps({"flag": False}, ensure_ascii=False), 400
    # If password is masked, don't overwrite
    if data.get("bind_password") == "******":
        data.pop("bind_password")
    ok = ldapinfo.updateLdapServer(name, data)
    if ok:
        msADauth.reload_config()
    return json.dumps({"flag": ok}, ensure_ascii=False)


@app.route("/ldap/servers/<name>", methods=["DELETE"])
def ldapServerDelete(name):
    denied = _require_admin()
    if denied:
        return denied
    ok = ldapinfo.deleteLdapServer(name)
    if ok:
        msADauth.reload_config()
    return json.dumps({"flag": ok}, ensure_ascii=False)


@app.route("/ldap/servers/test", methods=["POST"])
def ldapServerTest():
    denied = _require_admin()
    if denied:
        return denied
    data = request.json
    if not data or not data.get("host"):
        return json.dumps({"flag": False, "error": "host required"}, ensure_ascii=False), 400
    ok, msg = msADauth.test_connection(data)
    return json.dumps({"flag": ok, "message": msg}, ensure_ascii=False)


@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
