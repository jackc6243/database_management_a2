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
        curs.callproc('findAdmissionsByAdmin', [login])
        # curs.execute("""
        #     select AdmissionID, AdmissionTypeName, Department, DischargeDate, Fee, concat(FirstName, ' ', LastName) as PatientName, Condition
        #     from Admission join Patient on (Patient = PatientID) join AdmissionType on (AdmissionType = AdmissionTypeID)
        #     where Administrator = %s
        #     order by DischargeDate desc nulls last, PatientName asc, AdmissionType desc
        # """, (login,))

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
        # searchString = f"%{searchString}%"

        curs.callproc('findAdmissionsByCriteria', [searchString])
        # curs.execute("""
        #             SELECT
        #                 ad.AdmissionID,
        #                 adT.AdmissionTypeName,
        #                 dep.DeptName,
        #                 TO_CHAR(ad.DischargeDate, 'DD-MM-YYYY') as dis_date,
        #                 ad.Fee,
        #                 concat(p.FirstName, ' ', p.LastName) as full_name,
        #                 ad.condition
        #             FROM Admission ad
        #             JOIN AdmissionType adT on (adT.AdmissionTypeID = ad.admissiontype)
        #             join Department dep on (dep.DeptId = ad.Department)
        #             join patient p on (ad.Patient = p.PatientID)
        #             where
        #                 (lower(adT.AdmissionTypeName) like %s) or
        #                 (lower(dep.DeptName) like %s) or
        #                 (lower(p.FirstName) like %s) or
        #                 (lower(p.LastName) like %s) or
        #                 (lower(ad.condition) like %s)
        #             order by
        #                 to_char(ad.DischargeDate, 'YYYY-MM-DD') desc nulls first,
        #                 full_name asc
        #              """, (searchString, searchString, searchString, searchString, searchString,))

        rows = []
        row = curs.fetchone()
        while row is not None:
            rows.append({
                'admission_id': row[0],
                'admission_type': row[1],
                'admission_department': row[2],
                'discharge_date': row[3] if row[3] else "",
                'fee': row[4] if row[4] else "",
                'patient': row[5],
                'condition': row[6] if row[6] else "",
            })
            row = curs.fetchone()
        return rows
    except psycopg2.Error as sqle:
        print("sqle error", sqle)
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
        return False

    try:
        curs = conn.cursor()

        # Check if admission type is valid, if so obtain the admission type id
        curs.execute("""
                     SELECT AdmissionTypeID
                     FROM AdmissionType
                     WHERE lower(AdmissionTypeName) = lower(%s)
                     """, (type,))
        res = curs.fetchone()
        if res is None:
            print("Admission type not found")
            return False
        type_id = res[0]

        # check if department name is valid, if so obtai the department id
        curs.execute("""
                     SELECT DeptId
                     FROM Department
                     WHERE lower(DeptName) = lower(%s)
                     """, (department,))
        res = curs.fetchone()
        if res is None:
            print("Department name not found")
            return False
        dep_id = res[0]

        # insert into admissions
        curs.execute("""
                    insert into admission
                    (AdmissionType, Department, Patient, Administrator, Condition) VALUES
                    (%s, %s, %s, %s, %s);
                     """, (type_id, dep_id, patient.lower(), admin, condition))
        conn.commit()
        return True

    except psycopg2.Error as sqle:
        if conn:
            conn.rollback()
        print("Add admission error is:")
        print(sqle)
        return False
    finally:
        print("finally block")
        curs.close()
        conn.close()


'''
Update an existing admission
'''


def updateAdmission(id, type, department, dischargeDate, fee, patient, condition):

    return
