#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import json
import os
import sys

with open("password/password.json",'r') as f:
    passwd=json.load(f)

if os.getegid() != 0:
    if sys.argv[1] in passwd:
        oldPassword = input("Please enter the old password\n")    
        if hashlib.sha512(oldPassword.encode('utf-8')).hexdigest() == passwd[sys.argv[1]]:
            newPassword = input("Please enter the new password\n")
            newPassword2 = input("Please enter the new password again\n")
            if newPassword == newPassword2:
                passwd[sys.argv[1]] = hashlib.sha512(newPassword.encode('utf-8')).hexdigest()
                with open("password/password.json",'w') as f:
                    json.dump(passwd,f)
                print("Password changed successfully")
                
            else:
                print("The two entered passwords do not match")
                
        else:
            print("The old password is incorrect")
            
    else:
        print(f"{sys.argv[1]} is not a valid user")
else:
    if sys.argv[1] in passwd:
        newPassword = input("Please enter the new password\n")
        newPassword2 = input("Please enter the new password again\n")
        if newPassword == newPassword2:
            passwd[sys.argv[1]] = hashlib.sha512(newPassword.encode('utf-8')).hexdigest()
            with open("password/password.json",'w') as f:
                json.dump(passwd,f,indent=4)
            print("Password changed successfully")
            
        else:
            print("The two entered passwords do not match")
            
    else:
        flag = input(f'{sys.argv[1]} is not a valid user, do you want to add {sys.argv[1]} as a new user?(y to add, any other key to exit)\n')
        if flag == 'y':
            password = input(f'Please enter the password for {sys.argv[1]}\n')
            passwd[sys.argv[1]] = hashlib.sha512(password.encode('utf-8')).hexdigest()
            with open("password/password.json",'w') as f:
                json.dump(passwd,f,indent=4)
            print("Password changed successfully")
            