import os
import json
import mysql.connector


def linkStart():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "10.1.11.236"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "123qwe"),
        database=os.getenv("DB_NAME", "inspector"),
        port=int(os.getenv("DB_PORT", "5679")),
    )
    return connection


def ensureTable():
    """Create ldap_servers table if not exists."""
    connection = linkStart()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ldap_servers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(64) NOT NULL UNIQUE,
            host VARCHAR(255) NOT NULL,
            port INT DEFAULT 389,
            use_ssl TINYINT DEFAULT 0,
            bind_dn VARCHAR(255) DEFAULT '',
            bind_password VARCHAR(255) DEFAULT '',
            user_search_base VARCHAR(255) NOT NULL DEFAULT '',
            user_search_filter VARCHAR(255) DEFAULT '(sAMAccountName={username})',
            attr_username VARCHAR(64) DEFAULT 'sAMAccountName',
            attr_display_name VARCHAR(64) DEFAULT 'cn',
            attr_email VARCHAR(64) DEFAULT 'mail',
            role_mapping_admin VARCHAR(512) DEFAULT '',
            role_mapping_onduty VARCHAR(512) DEFAULT '',
            domains JSON NOT NULL
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()


def getLdapServers():
    """Return all LDAP server configs as list of dicts."""
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ldap_servers")
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    for row in results:
        if isinstance(row.get("domains"), str):
            try:
                row["domains"] = json.loads(row["domains"])
            except (json.JSONDecodeError, TypeError):
                row["domains"] = []
    return results


def getLdapServer(name):
    """Return single LDAP server config by name."""
    connection = linkStart()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ldap_servers WHERE name = %s", (name,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result and isinstance(result.get("domains"), str):
        try:
            result["domains"] = json.loads(result["domains"])
        except (json.JSONDecodeError, TypeError):
            result["domains"] = []
    return result


def addLdapServer(data):
    """Insert a new LDAP server config. Returns True on success."""
    connection = linkStart()
    cursor = connection.cursor()
    domains = data.get("domains", [])
    if isinstance(domains, list):
        domains = json.dumps(domains)
    try:
        cursor.execute(
            """INSERT INTO ldap_servers
            (name, host, port, use_ssl, bind_dn, bind_password,
             user_search_base, user_search_filter,
             attr_username, attr_display_name, attr_email,
             role_mapping_admin, role_mapping_onduty, domains)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                data["name"], data["host"], data.get("port", 389),
                int(data.get("use_ssl", 0)),
                data.get("bind_dn", ""), data.get("bind_password", ""),
                data.get("user_search_base", ""),
                data.get("user_search_filter", "(sAMAccountName={username})"),
                data.get("attr_username", "sAMAccountName"),
                data.get("attr_display_name", "cn"),
                data.get("attr_email", "mail"),
                data.get("role_mapping_admin", ""),
                data.get("role_mapping_onduty", ""),
                domains,
            ),
        )
        connection.commit()
        ok = True
    except Exception as e:
        print(e)
        ok = False
    cursor.close()
    connection.close()
    return ok


def updateLdapServer(name, data):
    """Update existing LDAP server config by name. Returns True on success."""
    connection = linkStart()
    cursor = connection.cursor()
    domains = data.get("domains")
    if isinstance(domains, list):
        domains = json.dumps(domains)

    fields = []
    values = []
    field_map = {
        "host": "host", "port": "port", "use_ssl": "use_ssl",
        "bind_dn": "bind_dn", "bind_password": "bind_password",
        "user_search_base": "user_search_base",
        "user_search_filter": "user_search_filter",
        "attr_username": "attr_username",
        "attr_display_name": "attr_display_name",
        "attr_email": "attr_email",
        "role_mapping_admin": "role_mapping_admin",
        "role_mapping_onduty": "role_mapping_onduty",
    }
    for key, col in field_map.items():
        if key in data:
            val = data[key]
            if key == "use_ssl":
                val = int(val)
            fields.append(f"{col} = %s")
            values.append(val)

    if domains is not None:
        fields.append("domains = %s")
        values.append(domains)

    if "new_name" in data:
        fields.append("name = %s")
        values.append(data["new_name"])

    if not fields:
        cursor.close()
        connection.close()
        return True

    values.append(name)
    try:
        cursor.execute(
            f"UPDATE ldap_servers SET {', '.join(fields)} WHERE name = %s",
            tuple(values),
        )
        connection.commit()
        ok = True
    except Exception as e:
        print(e)
        ok = False
    cursor.close()
    connection.close()
    return ok


def deleteLdapServer(name):
    """Delete LDAP server config by name."""
    connection = linkStart()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM ldap_servers WHERE name = %s", (name,))
        connection.commit()
        ok = cursor.rowcount > 0
    except Exception as e:
        print(e)
        ok = False
    cursor.close()
    connection.close()
    return ok
