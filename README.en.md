# Inspector

English | [中文](README.md)

A web-based dashboard for monitoring and managing [Supervisord](http://supervisord.org/) processes across multiple servers, with Microsoft Active Directory authentication.

## Features

- View Supervisord process status across multiple servers (connected / unreachable)
- Start and stop processes with fine-grained permission control
- Three-tier permission model: admin, on-duty, regular user
- AES-CBC encrypted password transport with one-time session keys

## Tech Stack

| Layer    | Technology                                   |
| -------- | -------------------------------------------- |
| Frontend | Vue 3 · TypeScript · Naive UI · Vite         |
| Backend  | Python 3.12 · Flask · Gunicorn               |
| Auth     | LDAP3 NTLM (Microsoft Active Directory)      |
| Database | MariaDB                                      |
| Process  | Supervisord XML-RPC                          |

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- MariaDB
- Supervisord running on target servers with XML-RPC enabled

### Local Development

```bash
# Backend
cd backend/app
pip install -r ../requirements.txt
python app.py           # listens on 0.0.0.0:5000

# Frontend (new terminal)
cd frontend
npm install
npm run dev             # listens on localhost:5173, /api proxied to :5000
```

### Docker Compose

```bash
docker compose up
```

### Kubernetes

```bash
kubectl apply -f deploy/k8s/inspector.yaml
```

## Configuration

Update the following files before running:

| File                               | Purpose                              |
| ---------------------------------- | ------------------------------------ |
| `backend/app/config.py`            | Supervisord RPC username / password  |
| `backend/app/auth.py`              | AD domain → domain controller IP map |
| `backend/app/model/serverinfo.py`  | Database connection settings         |
| `backend/app/model/userinfo.py`    | Database connection settings         |

## Database Schema

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

`userown` format: `{"server1": ["prog1", "group:prog2"]}`

## Architecture

```
Browser
  │  (served by Nginx)
Vue 3 SPA
  │  HTTP /api/*
Flask API  (Gunicorn :5000)
  ├── LDAP3      ──► Active Directory    (authentication)
  ├── XML-RPC    ──► Supervisord nodes   (process control)
  └── MariaDB    ──► inspectoruser / servers (permissions / registry)
```

## Permission Model

| Role                  | Visible Servers              | Controllable Processes       |
| --------------------- | ---------------------------- | ---------------------------- |
| Admin (`isadmin=1`)   | All                          | All                          |
| On-duty (`isonduty=1`)| AWS / NMG nodes              | All                          |
| Regular user          | Servers in `userown`         | Processes in `userown`       |

## License

MIT
