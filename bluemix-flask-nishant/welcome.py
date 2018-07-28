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

app = Flask(__name__, static_url_path='/static')


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
        sql = "select * from people;"
        stmt = ibm_db.prepare(db2conn, sql)
        ibm_db.execute(stmt)
        rows = []
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        print(rows)
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

    return render_template('index.html', data = rows, system_info = page, script_root = request.script_root)

@app.route('/delete/<name>')
def delete(name):
    db2conn = ibm_db.connect(
        "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(
            ibmdb2cred['port']) + ";UID=" +
        ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")

    if db2conn:
        sql = "DELETE FROM people WHERE name= ?"
        stmt = ibm_db.prepare(db2conn, sql)
        ibm_db.bind_param(stmt, 1, name)
        ibm_db.execute(stmt)
    ibm_db.close(db2conn)

    return "Success"

@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        data = request.form
        print(data['name'], data['keywords'])
        db2conn = ibm_db.connect(
            "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(ibmdb2cred['port']) + ";UID=" +
            ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")

        if db2conn:
            sql = "UPDATE people SET keywords = ? WHERE name = ?"
            stmt = ibm_db.prepare(db2conn, sql)
            ibm_db.bind_param(stmt, 1, data['keywords'])
            ibm_db.bind_param(stmt, 2, data['name'])
            ibm_db.execute(stmt)
        ibm_db.close(db2conn)

    return "Success"

@app.route('/search', methods=['POST','GET'])
def search():
    if request.method == 'POST':
        data = request.form
        db2conn = ibm_db.connect(
            "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(ibmdb2cred['port']) + ";UID=" +
            ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")

        if db2conn:
            if data['searchWord'] != '':
                sql = "select * from people where name = '" + (data['searchWord']) + "' or vehicle = '" + (data['searchWord']) + "' or room = '" + (data['searchWord']) +"' or telnum = '" + (data['searchWord']) + "' or keywords = '" + (data['searchWord']) + "' and  grade between " + (data['grade1']) + " and " + (data['grade2']) + " ;"
                stmt = ibm_db.exec_immediate(db2conn,sql)
            else:
                stmt = ibm_db.exec_immediate(db2conn,
                                             "SELECT * FROM people WHERE grade BETWEEN " + (data['grade1']) + " AND " + (data['grade2']))
            # fetch the result
            result = ibm_db.fetch_assoc(stmt)
            rows = []
            # fetch the result
            while result != False:
                rows.append(result.copy())
                result = ibm_db.fetch_assoc(stmt)

            jsonStr = json.dumps(rows)
            print ("\n\n###### before db close(JSON string) ######\n\n"+jsonStr)
            # close database connection
            ibm_db.close(db2conn)
            return json.jsonify(response = jsonStr)

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        db2conn = ibm_db.connect(
            "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(
                ibmdb2cred['port']) + ";UID=" +
            ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")
        if db2conn:
            with open(f.filename) as csvfile:
                csv_data = csv.reader(csvfile, delimiter=',')
                flag = 0
                for row in csv_data:
                    if flag:
                        sql = 'INSERT INTO people(course,section,instructor,room) VALUES(?, ?, ?, ?)'
                        print(sql,row)
                        stmt = ibm_db.prepare(db2conn, sql)
                        ibm_db.bind_param(stmt, 1, row[0])
                        ibm_db.bind_param(stmt, 2, row[1])
                        ibm_db.bind_param(stmt, 3, row[2])
                        ibm_db.bind_param(stmt, 4, row[3])
                        ibm_db.execute(stmt)
                    # close database connection
                    flag = 1
            ibm_db.close(db2conn)
            return 'file uploaded successfully'

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
