#!/usr/bin/env python3

import json
def readUser():
    with open("password/password.json",'r') as f:
        users=json.load(f)
    return users

def serversOfUser(user):
    with open("password/access.json",'r') as f:
        access=json.load(f)
    return access.get(user)