# Inspector

[English](README.en.md) | 中文

基于 Web 的 Supervisord 进程管理面板，支持跨多台服务器统一监控与操作，通过 Microsoft Active Directory 进行身份验证。

## 功能特性

- 跨多台服务器查看 Supervisord 进程状态（在线 / 离线）
- 启动、停止进程（基于细粒度权限控制）
- 三级权限模型：管理员、值班用户、普通用户
- AES-CBC 加密密码传输，密钥一次性生成

## 技术栈

| 层     | 技术                                      |
| ------ | ----------------------------------------- |
| 前端   | Vue 3 · TypeScript · Naive UI · Vite      |
| 后端   | Python 3.12 · Flask · Gunicorn            |
| 认证   | LDAP3 NTLM（Microsoft Active Directory）  |
| 数据库 | MariaDB                                   |
| 进程   | Supervisord XML-RPC                       |

## 快速开始

### 前置要求

- Python 3.12+
- Node.js 18+
- MariaDB
- 目标服务器上运行 Supervisord 并启用 XML-RPC

### 本地开发

```bash
# 后端
cd backend/app
pip install -r ../requirements.txt
python app.py           # 监听 0.0.0.0:5000

# 前端（新开终端）
cd frontend
npm install
npm run dev             # 监听 localhost:5173，/api 自动代理到 :5000
```

### Docker Compose

```bash
docker compose up
```

### Kubernetes

```bash
kubectl apply -f deploy/k8s/inspector.yaml
```

## 配置

运行前需修改以下文件中的参数：

| 文件                               | 内容                         |
| ---------------------------------- | ---------------------------- |
| `backend/app/config.py`            | Supervisord RPC 用户名/密码  |
| `backend/app/auth.py`              | AD 域名 → 域控服务器 IP 映射 |
| `backend/app/model/serverinfo.py`  | 数据库连接参数               |
| `backend/app/model/userinfo.py`    | 数据库连接参数               |

## 数据库 Schema

```sql
CREATE TABLE servers (
    servername VARCHAR(100) PRIMARY KEY,
    serveraddr VARCHAR(100),
    location   VARCHAR(100)
);

CREATE TABLE inspectoruser (
    username VARCHAR(100),
    domain   VARCHAR(100),
    isadmin  TINYINT DEFAULT 0,
    isonduty TINYINT DEFAULT 0,
    userown  JSON,
    PRIMARY KEY (username, domain)
);
```

`userown` 格式：`{"server1": ["prog1", "group:prog2"]}`

## 架构

```
浏览器
  │  (Nginx 静态服务)
Vue 3 SPA
  │  HTTP /api/*
Flask API  (Gunicorn :5000)
  ├── LDAP3      ──► Active Directory    （身份验证）
  ├── XML-RPC    ──► Supervisord nodes   （进程操作）
  └── MariaDB    ──► inspectoruser / servers （权限/注册表）
```

## 权限模型

| 角色                  | 可见服务器             | 可操作进程             |
| --------------------- | ---------------------- | ---------------------- |
| 管理员 (`isadmin=1`)  | 全部                   | 全部                   |
| 值班 (`isonduty=1`)   | AWS / NMG 节点         | 全部                   |
| 普通用户              | `userown` 配置的服务器 | `userown` 配置的进程   |

## License

MIT
