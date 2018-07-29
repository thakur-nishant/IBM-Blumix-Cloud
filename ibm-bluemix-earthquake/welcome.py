# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, render_template, redirect, request, json, jsonify, url_for
from werkzeug import secure_filename
import ibm_db
import csv

app = Flask(__name__)

ibmdb2cred = {
    "hostname": "dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net",
    "password": "nm6cfkf7z-h6zzvk",
    "https_url": "https://dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net",
    "port": 50000,
    "ssldsn": "DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net;PORT=50001;PROTOCOL=TCPIP;UID=vsq78514;PWD=nm6cfkf7z-h6zzvk;Security=SSL;",
    "host": "dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net",
    "jdbcurl": "jdbc:db2://dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net:50000/BLUDB",
    "uri": "db2://vsq78514:nm6cfkf7z-h6zzvk@dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net:50000/BLUDB",
    "db": "BLUDB",
    "dsn": "DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=vsq78514;PWD=nm6cfkf7z-h6zzvk;",
    "username": "vsq78514",
    "ssljdbcurl": "jdbc:db2://dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net:50001/BLUDB:sslConnection=true;"
}

@app.route('/')
def Welcome():
    db2conn = ibm_db.connect(
        "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(ibmdb2cred['port']) + ";UID=" +
        ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")

    if db2conn:
        # sql = "select * from earthquake Limit 20;"
        # stmt = ibm_db.prepare(db2conn, sql)
        # ibm_db.execute(stmt)
        # rows = []
        # # fetch the result
        # result = ibm_db.fetch_assoc(stmt)
        # while result != False:
        #     rows.append(result.copy())
        #     result = ibm_db.fetch_assoc(stmt)
        # # close database connection
        # print(rows)
        page = ""
        stmt = ibm_db.exec_immediate(db2conn,
                                     "select host_name,os_name,os_version,total_cpus,configured_cpus, total_memory,"
                                     "os_kernel_version,os_arch_type, os_release,os_full_version from sysibmadm.env_sys_info")
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        page += "OS Name: " + result["OS_NAME"] + "<br/>OS Version: " + result["OS_VERSION"]
        page += "<br/>Hostname: " + result["HOST_NAME"] + "<br/> Total CPUs: " + str(result["TOTAL_CPUS"])
        page += "<br/>Configured CPUs: " + str(result["CONFIGURED_CPUS"]) + "<br/>Total memory: " + str(
            result["TOTAL_MEMORY"]) + " MB"
        page += "<br/>OS Kernel Version: " + result["OS_KERNEL_VERSION"] + "<br/>OS Architecture Tpye: " + result[
            "OS_ARCH_TYPE"]
        page += "<br/>OS Release: " + result["OS_RELEASE"] + "<br/>OS full version: " + result["OS_FULL_VERSION"]
        ibm_db.close(db2conn)

    return render_template('index.html',system_info = page, script_root = request.script_root)
    # return render_template('index.html', data = rows, system_info = page, script_root = request.script_root)


@app.route('/searchMagnitude', methods=['POST','GET'])
def searchMagnitude():
    if request.method == 'POST':
        data = request.form
        db2conn = ibm_db.connect(
            "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(ibmdb2cred['port']) + ";UID=" +
            ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")

        if db2conn:
            stmt = ibm_db.exec_immediate(db2conn,
                                             "SELECT * FROM earthquake WHERE mag >" + data['searchWord'])
            # fetch the result
            result = ibm_db.fetch_assoc(stmt)
            rows = []
            # fetch the result
            while result != False:
                rows.append(result.copy())
                result = ibm_db.fetch_assoc(stmt)

            jsonStr = json.dumps(rows)
            # close database connection
            ibm_db.close(db2conn)
            return json.jsonify(response = jsonStr)


@app.route('/searchMagnitudeRange', methods=['POST','GET'])
def searchMagnitudeRange():
    if request.method == 'POST':
        data = request.form
        db2conn = ibm_db.connect(
            "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(ibmdb2cred['port']) + ";UID=" +
            ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")

        if db2conn:
            sql = "SELECT * FROM earthquake WHERE mag between " + data['range1'] + " and " + data['range2'] + " and TO_DATE(LEFT(time,10),'YYYY-MM-DD') BETWEEN '"+ data['startDate'] +"' AND '"+ data['endDate'] +"'";
            print(sql)
            stmt = ibm_db.exec_immediate(db2conn, sql)
            # fetch the result
            result = ibm_db.fetch_assoc(stmt)
            rows = []
            # fetch the result
            while result != False:
                rows.append(result.copy())
                result = ibm_db.fetch_assoc(stmt)

            jsonStr = json.dumps(rows)
            # close database connection
            ibm_db.close(db2conn)
            return json.jsonify(response = jsonStr)

@app.route('/searchMagnitudeIntervals', methods=['POST','GET'])
def searchMagnitudeIntervals():
    if request.method == 'POST':
        data = request.form
        db2conn = ibm_db.connect(
            "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(ibmdb2cred['port']) + ";UID=" +
            ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")

        if db2conn:
            pointer1 = int(data['range1'])
            endPoint = int(data['range2'])
            rows = []

            while pointer1 < endPoint :
                pointer2 = pointer1+0.1
                sql = "SELECT count(mag) FROM earthquake WHERE mag between " + str(pointer1+0.001)  + " and " + str(pointer2) +";"
                stmt = ibm_db.exec_immediate(db2conn, sql)
                # fetch the result
                result = ibm_db.fetch_assoc(stmt)
                # fetch the result
                rows.append([[pointer1, pointer2],result.copy()])

                pointer1 = pointer2

            jsonStr = json.dumps(rows)
            # close database connection
            ibm_db.close(db2conn)
            return json.jsonify(response = jsonStr)


@app.route('/searchLocation', methods=['POST','GET'])
def searchLocation():
    if request.method == 'POST':
        data = request.form
        db2conn = ibm_db.connect(
            "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(ibmdb2cred['port']) + ";UID=" +
            ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")

        if db2conn:
            # Reference : https://stackoverflow.com/questions/5031268/algorithm-to-find-all-latitude-longitude-locations-within-a-certain-distance-fro?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
            sql = "SELECT * FROM(SELECT *,(((acos(sin((" + data['latitude'] + "*(22/7)/180)) * sin((latitude*(22/7)/180))+cos((" + data['latitude'] + "*(22/7)/180)) * cos((latitude*(22/7)/180)) * cos(((" + data['longitude'] + " - longitude)*(22/7)/180))))*180/(22/7))*60*1.1515*1.609344) as distance FROM earthquake) t WHERE distance <= "+ data['distance']
            print(sql)
            
            stmt = ibm_db.exec_immediate(db2conn, sql)
            # fetch the result
            result = ibm_db.fetch_assoc(stmt)
            rows = []
            # fetch the result
            while result != False:
                rows.append(result.copy())
                result = ibm_db.fetch_assoc(stmt)

            jsonStr = json.dumps(rows)
            # close database connection
            ibm_db.close(db2conn)
            return json.jsonify(response = jsonStr)


@app.route('/searchLocationName', methods=['POST','GET'])
def searchLocationName():
    if request.method == 'POST':
        data = request.form
        db2conn = ibm_db.connect(
            "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(ibmdb2cred['port']) + ";UID=" +
            ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")

        if db2conn:
            # Reference : https://stackoverflow.com/questions/5031268/algorithm-to-find-all-latitude-longitude-locations-within-a-certain-distance-fro?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
            sql = "SELECT * FROM earthquake WHERE locationsource = '" + data['name'] + "' and mag between " + data['range1'] + " and " + data['range2']
            print(sql)
            
            stmt = ibm_db.exec_immediate(db2conn, sql)
            # fetch the result
            result = ibm_db.fetch_assoc(stmt)
            rows = []
            # fetch the result
            while result != False:
                rows.append(result.copy())
                result = ibm_db.fetch_assoc(stmt)

            jsonStr = json.dumps(rows)
            # close database connection
            ibm_db.close(db2conn)
            return json.jsonify(response = jsonStr)


@app.route('/searchLocationRange', methods=['POST','GET'])
def searchLocationRange():
    if request.method == 'POST':
        data = request.form
        db2conn = ibm_db.connect(
            "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(ibmdb2cred['port']) + ";UID=" +
            ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")

        if db2conn:
            sql = "SELECT * FROM earthquake WHERE latitude between " + data['latitude1'] + " and " + data['latitude2'] + " and longitude between " + data['longitude1'] + " and " + data['longitude2'] + ";"
            print(sql)
            
            stmt = ibm_db.exec_immediate(db2conn, sql)
            # fetch the result
            result = ibm_db.fetch_assoc(stmt)
            rows = []
            # fetch the result
            while result != False:
                rows.append(result.copy())
                result = ibm_db.fetch_assoc(stmt)

            jsonStr = json.dumps(rows)
            # close database connection
            ibm_db.close(db2conn)
            return json.jsonify(response = jsonStr)



@app.route('/myapp')
def WelcomeToMyapp():
    return 'Welcome again to my app running on Bluemix!'

@app.route('/api/people')
def GetPeople():
    list = [
        {'name': 'John', 'age': 28},
        {'name': 'Bill', 'val': 26}
    ]
    return jsonify(results=list)

@app.route('/api/people/<name>')
def SayHello(name):
    message = {
        'message': 'Hello ' + name
    }
    return jsonify(results=message)

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))

