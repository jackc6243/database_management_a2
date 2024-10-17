#!/usr/bin/env python3
import psycopg2
from flask import Flask

#####################################################
# Database Connection
#####################################################

'''
Connect to the database using the connection string
'''


def read_credentials():
    userid = None
    password = None

    with open('./secrets.txt', 'r') as f:
        lines = f.readlines()
        userid = lines[0].strip()
        password = lines[1].strip()

    return userid, password


def openConnection():
    # connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE
    userid, passwd = read_credentials()
    myHost = "awsprddbs4836.shared.sydney.edu.au"
    # Create a connection to the database
    conn = None
    try:
        # Parses the config file and connects using the connect string
        conn = psycopg2.connect(database=userid,
                                user=userid,
                                password=passwd,
                                host=myHost)

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)

    # return the connection to use
    return conn


'''
Validate staff based on username and password
'''


def checkLogin(username, password):
    conn = None
    try:
        conn = openConnection()
    except:
        print("Cannot open connection")
        conn.close()
        return None

    try:
        curs = conn.cursor()
        curs.execute("""
                     SELECT *
                     FROM Administrator
                     WHERE UserName = %s
                     AND password = %s
                     """, (username, password,))
        row = curs.fetchone()
        if row is None:
            return None
        return [row[0], row[2], row[3], row[4]]
    except psycopg2.Error as sqle:
        print(sqle)
        return None
    finally:
        print("finally block")
        curs.close()
        conn.close()

    # return ['jdoe', 'John', 'Doe', 'jdoe@csh.com']


'''
List all the associated admissions records in the database by staff
'''


def findAdmissionsByAdmin(login):

    return


'''
Find a list of admissions based on the searchString provided as parameter
See assignment description for search specification
'''


def findAdmissionsByCriteria(searchString):

    return


'''
Add a new addmission 
'''


def addAdmission(type, department, patient, condition, admin):

    return


'''
Update an existing admission
'''


def updateAdmission(id, type, department, dischargeDate, fee, patient, condition):

    return
