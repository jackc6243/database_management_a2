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
        print("psycopg2.Error : ", sqle)

    # return the connection to use
    return conn


'''
Validate staff based on username and password
'''


def checkLogin(username, password):
    conn = openConnection()
    if conn is None:
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
    conn = openConnection()
    if conn is None:
        return None

    try:
        curs = conn.cursor()
        curs.execute("""
            select AdmissionID, AdmissionTypeName, Department, DischargeDate, Fee, concat(FirstName, ' ', LastName) as PatientName, Condition
            from Admission join Patient on (Patient = PatientID) join AdmissionType on (AdmissionType = AdmissionTypeID)
            where Administrator = %s 
            order by DischargeDate desc nulls last, PatientName asc, AdmissionType desc
        """, (login,))

        rows = []
        row = curs.fetchone()
        while row is not None:
            admission = {
                'admission_id': row[0],
                'admission_type': row[1],
                'admission_department': row[2],
                'discharge_date': row[3] if row[3] else '',
                'fee': row[4] if row[4] else '',
                'patient': row[5],
                'condition': row[6] if row[6] else ''
            }
            rows.append(admission)
            row = curs.fetchone()

        return rows

    except psycopg2.Error as sqle:
        print(sqle)
        return None
    finally:
        print("finally block")
        curs.close()
        conn.close()


'''
Find a list of admissions based on the searchString provided as parameter
See assignment description for search specification
'''


def findAdmissionsByCriteria(searchString):
    conn = openConnection()
    if conn is None:
        return None

    try:
        curs = conn.cursor()
        searchString = f"%{searchString}%"
        curs.execute("""
                    SELECT
                        ad.AdmissionID,
                        adT.AdmissionTypeName,
                        dep.DeptName,
                        ad.DischargeDate,
                        ad.Fee,
                        p.FirstName,
                        p.LastName,
                        ad.condition
                    FROM Admission ad
                    JOIN AdmissionType adT on (adT.AdmissionTypeID = ad.admissiontype)
                    join Department dep on (dep.DeptId = ad.Department)
                    join patient p on (ad.Patient = p.PatientID)
                    where
                        (adT.AdmissionTypeName like %s) or
                        (dep.DeptName like %s) or
                        (p.FirstName like %s) or
                        (p.LastName like %s) or
                        (ad.condition like %s)
                     """, (searchString, searchString, searchString, searchString, searchString,))

        rows = []
        row = True
        while row is not None:
            row = curs.fetchone()
            rows.append({
                'admission_id': row[0],
                'admission_type': row[1],
                'admission_department': row[2],
                'discharge_date': row[3],
                'fee': row[4],
                'patient': f"{row[5]} {row[6]}",
                'condition': row[7]
            })
        return rows
    except psycopg2.Error as sqle:
        print(sqle)
        return None
    finally:
        print("finally block")
        curs.close()
        conn.close()


'''
Add a new addmission 
'''


def addAdmission(type, department, patient, condition, admin):
    conn = openConnection()
    if conn is None:
        return None

    try:
        curs = conn.cursor()
        curs.execute("""
                     SELECT *
                     FROM Administrator
                     WHERE UserName = %s
                     AND password = %s
                     """, (type, department, patient, condition, admin,))

    except psycopg2.Error as sqle:
        print(sqle)
        return None
    finally:
        print("finally block")
        curs.close()
        conn.close()


'''
Update an existing admission
'''


def updateAdmission(id, type, department, dischargeDate, fee, patient, condition):

    return
