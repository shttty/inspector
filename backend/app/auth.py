import os
import json
import yaml
from ldap3 import Server, Connection, SIMPLE, SUBTREE


_config_cache = None


def _resolve_env(obj):
    """Recursively replace ${VAR} placeholders with env var values."""
    if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
        return os.getenv(obj[2:-1], "")
    if isinstance(obj, dict):
        return {k: _resolve_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_env(i) for i in obj]
    return obj


def _load_file_config():
    """Load LDAP config from ldap.yml file. Returns empty dict on missing file."""
    config_path = os.environ.get(
        "LDAP_CONFIG",
        os.path.join(os.path.dirname(__file__), "ldap.yml"),
    )
    try:
        with open(config_path) as f:
            raw = yaml.safe_load(f) or {}
        return _resolve_env(raw)
    except FileNotFoundError:
        return {}


def _load_db_config():
    """Load LDAP server configs from database."""
    from model.ldapinfo import getLdapServers
    rows = getLdapServers()
    if not rows:
        return {}
    servers = []
    for row in rows:
        srv = {
            "name": row["name"],
            "host": row["host"],
            "port": row.get("port", 389),
            "use_ssl": bool(row.get("use_ssl", 0)),
            "bind_dn": row.get("bind_dn", ""),
            "bind_password": row.get("bind_password", ""),
            "user_search_base": row.get("user_search_base", ""),
            "user_search_filter": row.get("user_search_filter", "(sAMAccountName={username})"),
            "attributes": {
                "username": row.get("attr_username", "sAMAccountName"),
                "display_name": row.get("attr_display_name", "cn"),
                "email": row.get("attr_email", "mail"),
            },
            "role_mapping": {},
            "domains": [],
        }
        if row.get("role_mapping_admin"):
            srv["role_mapping"]["admin"] = row["role_mapping_admin"]
        if row.get("role_mapping_onduty"):
            srv["role_mapping"]["on_duty"] = row["role_mapping_onduty"]
        if row.get("domains"):
            domains = row["domains"]
            if isinstance(domains, str):
                try:
                    domains = json.loads(domains)
                except (json.JSONDecodeError, TypeError):
                    domains = [domains]
            srv["domains"] = domains
        servers.append(srv)
    return {"servers": servers}


def load_config(force=False):
    """Merge file config + DB config. DB entries override file entries by name."""
    global _config_cache
    if _config_cache is not None and not force:
        return _config_cache

    file_cfg = _load_file_config()
    db_cfg = _load_db_config()

    # Index file servers by name
    merged = {}
    for srv in file_cfg.get("servers", []):
        name = srv.get("name", srv.get("host", ""))
        merged[name] = srv

    # DB overrides file by name
    for srv in db_cfg.get("servers", []):
        name = srv.get("name", "")
        merged[name] = srv

    _config_cache = {"servers": list(merged.values())}
    return _config_cache


def reload_config():
    """Force reload config from file + DB. Call after DB config changes."""
    return load_config(force=True)


def _server_for_domain(domain):
    config = load_config()
    for srv in config.get("servers", []):
        if domain in srv.get("domains", []):
            return srv
    return None


def _map_role(cfg, groups):
    """Map LDAP group DNs to application role via config."""
    role_mapping = cfg.get("role_mapping", {})
    if not role_mapping:
        return "user"

    groups_lower = [g.lower() for g in groups]

    admin_dn = role_mapping.get("admin", "")
    if admin_dn and admin_dn.lower() in groups_lower:
        return "admin"

    onduty_dn = role_mapping.get("on_duty", "")
    if onduty_dn and onduty_dn.lower() in groups_lower:
        return "on_duty"

    return "user"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def userAuth(domain, username, password):
    """Authenticate via service-account bind -> search -> user rebind.

    Returns user info dict or None on failure.
    """
    cfg = _server_for_domain(domain)
    if not cfg:
        print(f"No LDAP server configured for domain: {domain}")
        return None

    host = cfg["host"]
    port = cfg.get("port", 389)
    use_ssl = cfg.get("use_ssl", False)
    ldap_server = Server(host, port=port, use_ssl=use_ssl)

    try:
        return _auth_bind_search(ldap_server, cfg, domain, username, password)
    except Exception as e:
        print(f"LDAP error for {username}@{domain}: {e}")
        return None


def search_users(domain, query="*"):
    """Search LDAP directory for users. Requires bind_dn in config."""
    cfg = _server_for_domain(domain)
    if not cfg:
        return []

    search_base = cfg.get("user_search_base", "")
    bind_dn = cfg.get("bind_dn", "")
    if not search_base or not bind_dn:
        return []

    ldap_server = Server(cfg["host"], port=cfg.get("port", 389), use_ssl=cfg.get("use_ssl", False))
    conn = Connection(ldap_server, user=bind_dn, password=cfg.get("bind_password", ""), authentication=SIMPLE)
    if not conn.bind():
        print("Service account bind failed for user search")
        return []

    attr_map = cfg.get("attributes", {})
    username_attr = attr_map.get("username", "sAMAccountName")
    dn_attr = attr_map.get("display_name", "cn")
    email_attr = attr_map.get("email", "mail")

    search_filter = f"(&(objectClass=user)(objectCategory=person)({username_attr}={query}))"
    conn.search(search_base, search_filter, search_scope=SUBTREE, attributes=[username_attr, dn_attr, email_attr, "memberOf"])

    users = []
    for entry in conn.entries:
        groups = [str(g) for g in entry.memberOf] if hasattr(entry, "memberOf") else []
        users.append({
            "username": str(getattr(entry, username_attr, "")),
            "display_name": str(getattr(entry, dn_attr, "")),
            "email": str(getattr(entry, email_attr, "")),
            "groups": groups,
            "role": _map_role(cfg, groups),
        })

    conn.unbind()
    return users


def test_connection(cfg):
    """Test LDAP connection with given config dict. Returns (ok, message)."""
    try:
        ldap_server = Server(cfg["host"], port=cfg.get("port", 389), use_ssl=cfg.get("use_ssl", False))
        bind_dn = cfg.get("bind_dn", "")
        bind_password = cfg.get("bind_password", "")
        if bind_dn:
            conn = Connection(ldap_server, user=bind_dn, password=bind_password, authentication=SIMPLE)
        else:
            conn = Connection(ldap_server)
        if not conn.bind():
            return False, f"Bind failed: {conn.last_error}"
        # Try a search if search_base configured
        search_base = cfg.get("user_search_base", "")
        if search_base:
            conn.search(search_base, "(objectClass=*)", search_scope=SUBTREE, size_limit=1)
        conn.unbind()
        return True, "Connection successful"
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Auth: service-account bind -> search user DN -> user rebind
# ---------------------------------------------------------------------------

def _auth_bind_search(server, cfg, domain, username, password):
    """Same pattern as Grafana, GitLab, Jenkins."""
    bind_dn = cfg.get("bind_dn", "")
    bind_password = cfg.get("bind_password", "")
    search_base = cfg.get("user_search_base", "")
    if not search_base:
        print(f"No user_search_base configured for domain: {domain}")
        return None

    search_filter = cfg.get(
        "user_search_filter", "(sAMAccountName={username})"
    ).format(username=username)

    attr_map = cfg.get("attributes", {})
    dn_attr = attr_map.get("display_name", "cn")
    email_attr = attr_map.get("email", "mail")
    ldap_attrs = ["distinguishedName", dn_attr, email_attr, "memberOf"]

    # Step 1: service account bind
    if bind_dn:
        svc = Connection(server, user=bind_dn, password=bind_password, authentication=SIMPLE)
    else:
        svc = Connection(server)

    if not svc.bind():
        print(f"Service account bind failed: {svc.last_error}")
        return None

    # Step 2: search for user
    svc.search(search_base, search_filter, search_scope=SUBTREE, attributes=ldap_attrs)
    if not svc.entries:
        print(f"User not found: {username}@{domain}")
        svc.unbind()
        return None

    entry = svc.entries[0]
    user_dn = entry.distinguishedName.value
    display_name = str(getattr(entry, dn_attr, username))
    email = str(getattr(entry, email_attr, ""))
    groups = [str(g) for g in entry.memberOf] if hasattr(entry, "memberOf") else []
    svc.unbind()

    # Step 3: bind as user to verify password
    user_conn = Connection(server, user=user_dn, password=password, authentication=SIMPLE)
    if not user_conn.bind():
        print(f"Auth failed for {username}@{domain}")
        return None
    user_conn.unbind()

    role = _map_role(cfg, groups)
    print(f"Auth succeeded: {username}@{domain} role={role}")

    return {
        "username": username,
        "domain": domain,
        "display_name": display_name,
        "email": email,
        "groups": groups,
        "role": role,
    }
