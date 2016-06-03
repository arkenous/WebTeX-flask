#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import json
import sqlite3
import subprocess

import os
from flask import Flask, render_template, session, request, redirect, jsonify
from ldap3 import Server, Connection, \
    AUTH_SIMPLE, STRATEGY_SYNC, GET_ALL_INFO, LDAPBindError
from werkzeug import utils
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = os.urandom(24)

base = os.path.dirname(os.path.abspath(__file__))
conf = base + '/WebTeX.ini'
db = base + '/WebTeX.db'
storage = base + '/static/storage/'


@app.before_request
def before_request():
    config = configparser.ConfigParser()
    config.read(conf)
    initial_setup = config['setup']['initial_setup']
    if initial_setup == 'true' and not (
            request.path == '/readConfig' or request.path == '/saveConfig'):
        return render_template('initialize.html')
    if initial_setup == 'true' and (
            request.path == '/readConfig' or request.path == '/saveConfig'):
        return
    if initial_setup == 'false' and (
            request.path == '/readConfig' or request.path == '/saveConfig'):
        return redirect('/logout')

    if session.get('username') is not None:
        return
    if request.path == '/login':
        return
    return redirect('/login')


@app.route('/readConfig', methods=['POST'])
def read_config():
    dictionary = {}
    config = configparser.ConfigParser()
    config.read(conf)
    dictionary['mode'] = config['auth']['method']
    dictionary['ldap_address'] = config['ldap']['server']
    dictionary['ldap_port'] = config['ldap']['port']
    dictionary['ldap_basedn'] = config['ldap']['base_dn']
    dictionary['java_home'] = config['redpen']['java_home']
    dictionary['redpen_conf_path'] = config['redpen']['conf']
    dictionary['result'] = 'Success'
    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/saveConfig', methods=['POST'])
def save_config():
    dictionary = {}
    config = configparser.ConfigParser()
    config.read(conf)
    config['setup']['initial_setup'] = 'false'
    config['auth']['method'] = request.json['mode']
    config['ldap']['server'] = request.json['ldap_address']
    config['ldap']['port'] = request.json['ldap_port']
    config['ldap']['basedn'] = request.json['ldap_basedn']
    config['redpen']['java_home'] = request.json['java_home']
    config['redpen']['conf'] = request.json['redpen_conf_path']
    f = open(conf, 'w')
    config.write(f)
    f.close()
    dictionary['result'] = 'Success'
    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and is_account_valid():
        session['username'] = request.form['username']
        return redirect('/')
    return render_template('login.html')


def is_account_valid():
    username = request.form['username']
    config = configparser.ConfigParser()
    config.read(conf)

    if config['auth']['method'] == 'ldap':
        server = config['ldap']['server']
        port = int(config['ldap']['port'])
        base_dn = config['ldap']['base_dn']
        user_dn = 'uid=' + username + ',' + base_dn

        s = Server(server, port=port, get_info=GET_ALL_INFO)
        try:
            Connection(s, auto_bind=True, client_strategy=STRATEGY_SYNC,
                       user=user_dn, password=request.form['password'],
                       authentication=AUTH_SIMPLE, check_names=True)
            return True
        except LDAPBindError:
            return False
    elif config['auth']['method'] == 'local':
        con = sqlite3.connect(db)
        cur = con.cursor()
        sql = 'SELECT password FROM user WHERE username=(?)'
        cur.execute(sql, (username,))
        fetched = cur.fetchone()
        if fetched is None:
            return False
        hashedpass = fetched[0]
        if check_password_hash(hashedpass, request.form['password']):
            return True
        else:
            return False


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


@app.route('/readDirectory', methods=['POST'])
def read_directory():
    dictionary = {}
    if not os.path.exists(storage) or not os.path.isdir(storage):
        os.mkdir(storage)

    user_storage = storage + session['username']
    if os.path.exists(user_storage) and os.path.isdir(user_storage):
        dictionary['name'] = os.listdir(user_storage)
    else:
        os.mkdir(user_storage)
        dictionary['name'] = ''

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/createDirectory', methods=['POST'])
def create_directory():
    project = storage + session['username'] + '/' + request.json['name']
    os.mkdir(project)
    return jsonify()


@app.route('/setDirectory', methods=['POST'])
def set_directory():
    dictionary = {}
    session['cwd'] = storage + session['username'] + '/' + request.json['name']
    os.chdir(session.get('cwd'))
    if os.path.exists(session['cwd']) and os.path.isdir(session['cwd']):
        dictionary['result'] = 'Success'
        # if document.tex exist, read it.
        if os.path.exists(session['cwd'] + '/document.tex'):
            text = open(session['cwd'] + '/document.tex').read()
            dictionary['exist'] = 'True'
            dictionary['text'] = text
        else:
            dictionary['exist'] = 'False'
    else:
        session['cwd'] = ''
        dictionary = {'result': 'Failure'}

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/readFilelist', methods=['POST'])
def read_filelist():
    dictionary = {}
    if session.get('cwd') == '' or session.get('cwd') is None:
        dictionary['result'] = 'Failure'
    else:
        dictionary['result'] = 'Success'
        dictionary['list'] = os.listdir(session['cwd'])
        dictionary['username'] = session['username']
        if os.path.exists(os.path.join(session['cwd'], 'document.tex')):
            dictionary['tex'] = 'True'
            if os.path.exists(os.path.join(session['cwd'], 'document.pdf')):
                dictionary['pdf'] = 'True'
            else:
                dictionary['pdf'] = 'False'
        else:
            dictionary['tex'] = 'False'

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/upload', methods=['POST'])
def upload_file():
    dictionary = {}
    if session.get('cwd') == '' or session.get('cwd') is None:
        dictionary['result'] = 'Failure'
    else:
        file = request.files['file']
        if file:
            filename = utils.secure_filename(file.filename)
            file.save(os.path.join(session.get('cwd'), filename))
            dictionary['result'] = 'Success'
        else:
            dictionary['result'] = 'Failure'

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/compile', methods=['POST'])
def compile_tex():
    dictionary = {}
    if session.get('cwd') == '' or session.get('cwd') is None:
        dictionary['result'] = 'Failure'
    else:
        dictionary['result'] = 'Success'
        text = request.json['text']
        os.chdir(session['cwd'])
        f = open('document.tex', 'w')
        f.write(text)
        f.close()

        dictionary['texlog'] = subprocess.check_output(
            ['platex', '-halt-on-error', '-interaction=nonstopmode',
             '-file-line-error', '-no-shell-escape', 'document.tex'
             ]).decode('utf-8').splitlines()
        subprocess.check_output(
            ['dvipdfmx', 'document.dvi']).decode('utf-8').splitlines()
        if os.path.exists('document.pdf'):
            dictionary['existpdf'] = 'True'
            dictionary['user'] = session['username']
            config = configparser.ConfigParser()
            config.read(conf)
            os.environ['JAVA_HOME'] = config['redpen']['java_home']
            subprocess.call(['pdftotext', 'document.pdf', 'document.txt'])
            redpen = subprocess.Popen(
                ['redpen', '-c', config['redpen']['conf'], 'document.txt'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()
            dictionary['redpenout'] = redpen[0].decode('utf-8').splitlines()
            dictionary['redpenerr'] = redpen[1].decode('utf-8').splitlines()
        else:
            dictionary['existpdf'] = 'False'

    return jsonify(ResultSet=json.dumps(dictionary))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
